import os
import sys
import shutil
import logging
import webbrowser
import traceback
import socket

import django.conf
from django.template.loader import add_to_builtins

from cactus import ui as ui_module
from cactus.config.router import ConfigRouter
from cactus.deployment.gcs.engine import GCSDeploymentEngine
from cactus.deployment.s3.engine import S3DeploymentEngine
from cactus.i18n.commands import MessageMaker, MessageCompiler
from cactus.plugin.builtin.cache import CacheDurationPlugin
from cactus.plugin.builtin.context import ContextPlugin
from cactus.plugin.builtin.ignore import IgnorePatternsPlugin
from cactus.plugin.loader import CustomPluginsLoader, ObjectsPluginLoader
from cactus.plugin.manager import PluginManager
from cactus.static.external.manager import ExternalManager
from cactus.compat.paths import SiteCompatibilityLayer
from cactus.compat.page import PageContextCompatibilityPlugin
from cactus.utils.file import fileSize
from cactus.utils.filesystem import fileList
from cactus.utils.helpers import memoize
from cactus.utils.network import internetWorking
from cactus.utils.parallel import multiMap, PARALLEL_DISABLED, PARALLEL_CONSERVATIVE, PARALLEL_AGGRESSIVE
from cactus.utils.url import is_external
from cactus.page import Page
from cactus.static import Static
from cactus.listener import Listener
from cactus.server import Server, RequestHandler
from cactus.browser import browserReload, browserReloadCSS


class Site(SiteCompatibilityLayer):
    _path = None
    _parallel = PARALLEL_CONSERVATIVE  #TODO: Test me
    _static = None

    def __init__(self, path, config_paths=None, ui=None,
        PluginManagerClass=None, ExternalManagerClass=None, DeploymentEngineClass=None):

        # Load the config engine
        if config_paths is None:
            config_paths = []
        self.config = ConfigRouter(config_paths)

        # Load site-specific config values
        self.prettify_urls = self.config.get('prettify', False)
        self.fingerprint_extensions = self.config.get('fingerprint', [])
        self.locale = self.config.get("locale", None)

        # Verify our location looks correct
        self.path = path
        self.verify_path()

        # Load Managers
        if ui is None:
            ui = ui_module
        self.ui = ui

        if PluginManagerClass is None:
            PluginManagerClass =  PluginManager
        self.plugin_manager = PluginManagerClass(self,
            [
                CustomPluginsLoader(self.plugin_path),  # User plugins
                ObjectsPluginLoader([   # Builtin plugins
                    ContextPlugin(), CacheDurationPlugin(),
                    IgnorePatternsPlugin(), PageContextCompatibilityPlugin(),
                ])
            ]
        )

        if ExternalManagerClass is None:
            ExternalManagerClass = ExternalManager
        self.external_manager = ExternalManagerClass(self)

        hosting_provider = self.config.get("host", "aws")
        assert hosting_provider in ["aws", "gce"], "Invalid hosting provider"  #TODO: Make this dynamic using a dict...

        if hosting_provider == "aws":
            DefaultDeploymentEngineClass = S3DeploymentEngine
        elif hosting_provider == "gce":
            DefaultDeploymentEngineClass = GCSDeploymentEngine

        if DeploymentEngineClass is None:
            DeploymentEngineClass = DefaultDeploymentEngineClass
        self.deployment_engine = DeploymentEngineClass(self)

        # Load Django settings
        self.setup()

    @property
    def url(self):
        return self.config.get('site-url')

    @url.setter
    def url(self, value):
        self.config.set('site-url', value)
        self.config.write()

    def verify_url(self):
        """
        We need the site url to generate the sitemap.
        """
        #TODO: Make a "required" option in the config.
        #TODO: Use URL tags in the sitemap

        if self.url is None:
            self.url = self.ui.prompt_url("Enter your site URL (e.g. http://example.com/)")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

        self.build_path = os.path.join(path, '.build')
        self.template_path = os.path.join(path, 'templates')
        self.page_path = os.path.join(path, 'pages')
        self.plugin_path = os.path.join(path, 'plugins')
        self.static_path = os.path.join(path, 'static')
        self.script_path = os.path.join(os.getcwd(), __file__)
        self.locale_path = os.path.join(path, "locale")


    def setup(self):
        """
        Configure django to use both our template and pages folder as locations
        to look for included templates.
        """

        settings = {
            "TEMPLATE_DIRS": [self.template_path, self.page_path],
            "INSTALLED_APPS": ['django.contrib.markup'],
        }

        if self.locale is not None:
            settings.update({
                "USE_I18N": True,
                "USE_L10N": False,
                "LANGUAGE_CODE":  self.locale,
                "LOCALE_PATHS": [self.locale_path],
            })

        django.conf.settings.configure(**settings)

        add_to_builtins('cactus.template_tags')

    def verify_path(self):
        """
        Check if this path looks like a Cactus website
        """
        required_subfolders = ['pages', 'static', 'templates', 'plugins']
        if self.locale is not None:
            required_subfolders.append('locale')

        for p in required_subfolders:
            if not os.path.isdir(os.path.join(self.path, p)):
                logging.info('This does not look like a (complete) cactus project (missing "%s" subfolder)', p)
                sys.exit(1)

    @memoize
    def context(self):
        """
        Base context for the site: all the html pages.
        """
        ctx = {
            'CACTUS': {'pages': [p for p in self.pages() if p.is_html()]},
            '__CACTUS_SITE__': self,
        }
        return ctx

    def make_messages(self):
        """
        Generate the .po files for the site.
        """
        if self.locale is None:
            logging.error("You should set a locale in your configuration file before running this command.")
            return

        message_maker = MessageMaker(self)
        message_maker.execute()

    def compile_messages(self):
        """
        Remove pre-existing compiled language files, and re-compile.
        """
        #TODO: Make this cleaner
        mo_path = os.path.join(self.locale_path, self.locale, "LC_MESSAGES", "django.mo")
        try:
            os.remove(mo_path)
        except OSError:
            # No .mo file yet
            pass

        message_compiler = MessageCompiler(self)
        message_compiler.execute()

    def clean(self):
        """
        Remove all build files.
        """
        if os.path.isdir(self.build_path):
            shutil.rmtree(self.build_path)

    def build(self):
        """
        Generate fresh site from templates.
        """
        self.verify_url()

        #TODO: Facility to reset the site, and reload config.
        #TODO: Currently, we can't build a site instance multiple times
        self.plugin_manager.reload()  # Reload in case we're running on the server # We're still loading twice!

        self.plugin_manager.preBuild(self)

        logging.info('Plugins:    %s', ', '.join([p.plugin_name for p in self.plugin_manager.plugins]))
        logging.info('Processors: %s', ', '.join([p.__name__ for p in self.external_manager.processors]))
        logging.info('Optimizers: %s', ', '.join([p.__name__ for p in self.external_manager.optimizers]))

        # Make sure the build path exists
        if not os.path.exists(self.build_path):
            os.mkdir(self.build_path)

        # Prepare translations
        if self.locale is not None:
            self.compile_messages()
            #TODO: Check the command actually completes (msgfmt might not be on the PATH!)

        # Copy the static files
        self.buildStatic()

        # Render the pages to their output files

        mapper = map
        if self._parallel >= PARALLEL_AGGRESSIVE:
            mapper = multiMap

        mapper(lambda p: p.build(), self.pages())

        self.plugin_manager.postBuild(self)

        for static in self.static():
            shutil.rmtree(static.pre_dir)

    def static(self):
        """
        Retrieve a list of static files for the site
        """
        if self._static is None:
            paths = fileList(self.static_path, relative=True)
            self._static = [Static(self, path) for path in paths]
        return self._static

    def _get_url(self, src_url, resources):
        if is_external(src_url):
            return src_url

        resources_dict = dict((resource.link_url, resource) for resource in resources)

        try:
            return resources_dict[src_url].final_url
        except KeyError:
            raise Exception('Resource does not exist: {0}'.format(src_url))

    def get_url_for_static(self, src_path):
        return self._get_url(src_path, self.static())

    def get_url_for_page(self, src_path):
        return self._get_url(src_path, self.pages())

    def buildStatic(self):
        """
        Build static files (pre-process, copy to static folder)
        """
        mapper = multiMap
        if self._parallel <= PARALLEL_DISABLED:
            mapper = map

        mapper(lambda s: s.build(), self.static())

    @memoize
    def pages(self):
        """
        List of pages.
        """
        paths = fileList(self.page_path, relative=True)
        paths = filter(lambda x: not x.endswith("~"), paths)
        return [Page(self, p) for p in paths]

    def serve(self, browser=True, port=8000):
        """
        Start a http server and rebuild on changes.
        """
        self.clean()
        self.build()

        logging.info('Running webserver at 0.0.0.0:%s for %s' % (port, self.build_path))
        logging.info('Type control-c to exit')

        os.chdir(self.build_path)

        def rebuild(changes):
            logging.info('*** Rebuilding (%s changed)' % self.path)

            # We will pause the listener while building so scripts that alter the output
            # like coffeescript and less don't trigger the listener again immediately.
            self.listener.pause()
            try:
                self.build()
            except Exception, e:
                logging.info('*** Error while building\n%s', e)
                traceback.print_exc(file=sys.stdout)

            # When we have changes, we want to refresh the browser tabs with the updates.
            # Mostly we just refresh the browser except when there are just css changes,
            # then we reload the css in place.
            if len(changes["added"]) == 0 and \
                    len(changes["deleted"]) == 0 and \
                    set(map(lambda x: os.path.splitext(x)[1], changes["changed"])) == set([".css"]):
                browserReloadCSS('http://127.0.0.1:%s' % port)
            else:
                browserReload('http://127.0.0.1:%s' % port)

            self.listener.resume()

        self.listener = Listener(self.path, rebuild, ignore=lambda x: '/.build/' in x)
        self.listener.run()

        try:
            httpd = Server(("", port), RequestHandler)
        except socket.error:
            logging.info('Could not start webserver, port is in use. To use another port:')
            logging.info('  cactus serve %s' % (int(port) + 1))
            return

        if browser is True:
            webbrowser.open('http://127.0.0.1:%s' % port)

        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            httpd.server_close()

        logging.info('See you!')

    def upload(self):
        # Make sure we have internet
        if not internetWorking():
            logging.info('There does not seem to be internet here, check your connection')
            return

        logging.debug('Start upload')

        self.clean()
        self.build()

        self.plugin_manager.preDeploy(self)

        totalFiles = self.deployment_engine.deploy()
        changedFiles = [r for r in totalFiles if r['changed']]

        self.plugin_manager.postDeploy(self)

        # Display done message and some statistics
        logging.info('\nDone\n')

        logging.info('%s total files with a size of %s' %
                     (len(totalFiles), fileSize(sum([r['size'] for r in totalFiles]))))
        logging.info('%s changed files with a size of %s' %
                     (len(changedFiles), fileSize(sum([r['size'] for r in changedFiles]))))

        logging.info('\nhttp://%s\n' % self.config.get('aws-bucket-website'))
