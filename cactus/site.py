import os
import sys
import shutil
import logging
import webbrowser
import traceback
import socket

import django.conf

from cactus import ui as ui_module
from cactus.config.router import ConfigRouter
from cactus.deployment import get_deployment_engine_class
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
from cactus.utils.helpers import memoize, map_apply
from cactus.utils.network import internetWorking
from cactus.utils.parallel import multiMap, PARALLEL_DISABLED, PARALLEL_CONSERVATIVE, PARALLEL_AGGRESSIVE
from cactus.utils.url import is_external
from cactus.page import Page
from cactus.static import Static
from cactus.listener import Listener
# from cactus.server import Server, RequestHandler
from cactus.server import WebServer
from cactus.browser import browserReload, browserReloadCSS
from cactus.utils import ipc


logger = logging.getLogger(__name__)

DEFAULT_PROVIDER = "aws"


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
        self.compress_extensions = self.config.get('compress', ['html', 'css', 'js', 'txt', 'xml'])
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

        if DeploymentEngineClass is None:
            hosting_provider = self.config.get("provider", DEFAULT_PROVIDER)
            DeploymentEngineClass = get_deployment_engine_class(hosting_provider)
            assert DeploymentEngineClass is not None, \
                   "Could not load Deployment for Provider: {0}".format(hosting_provider)
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

        # if self.url is None:
        #     self.url = self.ui.prompt_url("Enter your site URL (e.g. http://example.com/)")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

        self.build_path = os.path.join(path, '.build')
        self.deploy_path = os.path.join(path, '.deploy')
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
            "INSTALLED_APPS": ['django_markwhat'],
        }

        if self.locale is not None:
            settings.update({
                "USE_I18N": True,
                "USE_L10N": False,
                "LANGUAGE_CODE":  self.locale,
                "LOCALE_PATHS": [self.locale_path],
            })

        django.conf.settings.configure(**settings)

        # - Importing here instead of the top-level makes it work on Python 3.x (!)
        # - loading add_to_builtins from loader implictly loads the loader_tags built-in
        # - Injecting our tags using add_to_builtins ensures that Cactus tags don't require an import
        from django.template.loader import add_to_builtins
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
                logger.error('This does not look like a (complete) cactus project (missing "%s" subfolder)', p)
                sys.exit(1)

    @memoize
    def context(self):
        """
        Base context for the site: all the html pages.
        """
        ctx = {
            'CACTUS': {
                'pages':  [p for p in self.pages() if p.is_html()],
                'static': [p for p in self.static()]
            },
            '__CACTUS_SITE__': self,
        }

        # Also make lowercase work
        ctx['cactus'] = ctx['CACTUS']

        return ctx

    def make_messages(self):
        """
        Generate the .po files for the site.
        """
        if self.locale is None:
            logger.error("You should set a locale in your configuration file before running this command.")
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
        logger.debug("*** CLEAN %s", self.path)

        if os.path.isdir(self.build_path):
            shutil.rmtree(self.build_path)

    def build(self):
        """
        Generate fresh site from templates.
        """

        logger.debug("*** BUILD %s", self.path)

        self.verify_url()

        # Reset the static content
        self._static = None

        #TODO: Facility to reset the site, and reload config.
        #TODO: Currently, we can't build a site instance multiple times
        self.plugin_manager.reload()  # Reload in case we're running on the server # We're still loading twice!

        self.plugin_manager.preBuild(self)

        logger.debug('Plugins:    %s', ', '.join([p.plugin_name for p in self.plugin_manager.plugins]))
        logger.debug('Processors: %s', ', '.join([p.__name__ for p in self.external_manager.processors]))
        logger.debug('Optimizers: %s', ', '.join([p.__name__ for p in self.external_manager.optimizers]))

        # Make sure the build path exists
        if not os.path.exists(self.build_path):
            os.mkdir(self.build_path)

        # Prepare translations
        if self.locale is not None:
            self.compile_messages()
            #TODO: Check the command actually completes (msgfmt might not be on the PATH!)

        # Copy the static files
        self.buildStatic()

        # Always clean out the pages

        build_static_path = os.path.join(self.build_path, "static")

        for path in os.listdir(self.build_path):
            path = os.path.join(self.build_path, path)
            if path != build_static_path:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

        # Render the pages to their output files
        mapper = multiMap if self._parallel >= PARALLEL_AGGRESSIVE else map_apply
        mapper(lambda p: p.build(), self.pages())

        self.plugin_manager.postBuild(self)

        for static in self.static():
            if os.path.isdir(static.pre_dir):
                shutil.rmtree(static.pre_dir)

    def static(self):
        """
        Retrieve a list of static files for the site
        """
        if self._static is None:

            self._static = []

            for path in fileList(self.static_path, relative=True):

                full_path = os.path.join(self.static_path, path)

                if os.path.islink(full_path):
                    if not os.path.exists(os.path.realpath(full_path)):
                        logger.warning("Skipping symlink that points to unexisting file:\n%s", full_path)
                        continue

                self._static.append(Static(self, path))

        return self._static

    def _get_resource(self, src_url, resources):

        if is_external(src_url):
            return src_url

        for split_char in ["#", "?"]:
            if split_char in src_url:
                src_url = src_url.split(split_char)[0]

        resources_dict = dict((resource.link_url, resource) for resource in resources)

        if src_url in resources_dict:
            return resources_dict[src_url].final_url

        return None


    def _get_url(self, src_url, resources):
        return self._get_resource(src_url, resources)

    def get_url_for_static(self, src_path):
        return self._get_url(src_path, self.static())

    def get_url_for_page(self, src_path):
        return self._get_url(src_path, self.pages())

    def buildStatic(self):
        """
        Build static files (pre-process, copy to static folder)
        """
        mapper = multiMap if self._parallel > PARALLEL_DISABLED else map_apply
        mapper(lambda s: s.build(), self.static())

    def pages(self):
        """
        List of pages.
        """

        if not hasattr(self, "_page_cache"):
            self._page_cache = {}

        pages = []

        for path in fileList(self.page_path, relative=True):

            if path.endswith("~"):
                continue

            if path not in self._page_cache:
                logger.debug("Found page: %s", path)
                self._page_cache[path] = Page(self, path)

            pages.append(self._page_cache[path])

        return pages

    def _rebuild_should_ignore(self, file_path):

        file_relative_path = os.path.relpath(file_path, self.path)

        # Ignore anything in a hidden folder like .git
        for path_part in file_relative_path.split(os.path.sep):
            if path_part.startswith("."):
                return True

        if file_path.startswith(self.page_path):
            return False

        if file_path.startswith(self.template_path):
            return False

        if file_path.startswith(self.static_path):
            return False

        if file_path.startswith(self.plugin_path):
            return False

        return True

    def _rebuild(self, changes):

        logger.debug("*** REBUILD %s", self.path)

        logger.info('*** Rebuilding (%s changed)' % self.path)

        # We will pause the listener while building so scripts that alter the output
        # like coffeescript and less don't trigger the listener again immediately.
        self.listener.pause()

        try:
            #TODO: Fix this.
            #TODO: The static files should handle collection of their static folder on their own
            #TODO: The static files should not run everything on __init__
            #TODO: Only rebuild static files that changed
            # We need to "clear out" the list of static first. Otherwise, processors will not run again
            # They run on __init__ to run before fingerprinting, and the "built" static files themselves,
            # which are in a temporary folder, have been deleted already!
            # self._static = None
            self.build()

        except Exception as e:
            logger.info('*** Error while building\n%s', e)
            traceback.print_exc(file=sys.stdout)

        changed_file_extension = set(map(lambda x: os.path.splitext(x)[1], changes["changed"]))
        reload_css_file_extenstions = set([".css", ".sass", ".scss", ".styl"])

        # When we have changes, we want to refresh the browser tabs with the updates.
        # Mostly we just refresh the browser except when there are just css changes,
        # then we reload the css in place.

        local_hosts = [
            "http://127.0.0.1:%s" % self._port,
            "http://localhost:%s" % self._port,
            "http://0.0.0.0:%s" % self._port
        ]

        if len(changes["added"]) == 0 and len(changes["deleted"]) == 0 and changed_file_extension.issubset(reload_css_file_extenstions):
            # browserReloadCSS(local_hosts)
            self.server.reloadCSS()
        else:
            # browserReload(local_hosts)
            self.server.reloadPage()

        self.listener.resume()

    def serve(self, browser=True, port=8000):
        """
        Start a http server and rebuild on changes.
        """
        self._parallel = PARALLEL_DISABLED
        self._port = port

        self.clean()
        self.build()

        logger.info('Running webserver at http://127.0.0.1:%s for %s' % (port, self.build_path))
        ipc.signal("server.didstart")
        logger.info('Type control-c to exit')

        os.chdir(self.build_path)

        self.listener = Listener(self.path, self._rebuild, ignore=self._rebuild_should_ignore)
        self.listener.run()

        self.server = WebServer(self.build_path, port=port)

        try:
            self.server.start()

            # if browser is True:
            #     webbrowser.open('http://127.0.0.1:%s' % port)

        except (KeyboardInterrupt, SystemExit):
            self.server.stop()
            logger.info("Bye")

    def upload(self):

        # Make sure we have internet
        if not internetWorking():
            logger.info('There does not seem to be internet here, check your connection')
            return

        logger.debug('Start upload')

        self.build_path = self.deploy_path

        self.clean()
        self.build()

        self.plugin_manager.preDeploy(self)

        totalFiles = self.deployment_engine.deploy()
        changedFiles = [r for r in totalFiles if r['changed']]

        self.plugin_manager.postDeploy(self)

        # Display done message and some statistics
        logger.info('\nDone\n')

        logger.info('%s total files with a size of %s' %
                     (len(totalFiles), fileSize(sum([r['size'] for r in totalFiles]))))
        logger.info('%s changed files with a size of %s' %
                     (len(changedFiles), fileSize(sum([r['size'] for r in changedFiles]))))

        logger.info('\nhttp://%s\n' % self.config.get('aws-bucket-website'))  #TODO: Fix


    def domain_setup(self):

        # Make sure we have internet
        if not internetWorking():
            logger.info('There does not seem to be internet here, check your connection')
            return

        self.deployment_engine.domain_setup()
        self.domain_list()

    def domain_list(self):
        self.deployment_engine.domain_list()
