import os
import codecs
import logging
import copy
import urlparse

from django.template import Template, Context

from cactus.utils import parseValues


class Page(object):
    def __init__(self, site, source_path):
        self.site = site

        # The path where this element should be linked in "base" pages
        self.source_path = source_path

        # The URL where this element should be linked in "base" pages
        self.link_url = '/{0}'.format(self.source_path)

        if self.site.prettify_urls:
            # The URL where this element should be linked in "built" pages
            if self.is_html():
                if self.is_index():
                    self.final_url = self.link_url.rsplit('index.html', 1)[0]
                else:
                    self.final_url = '{0}/'.format(self.link_url.rsplit('.html', 1)[0])
            else:
                self.final_url = self.link_url

            # The path where this element should be built to
            if not self.is_html() or self.source_path.endswith('index.html'):
                self.build_path = self.source_path
            else:
                self.build_path = '{0}/{1}'.format(self.source_path.rsplit('.html', 1)[0], 'index.html')
        else:
            self.final_url = self.link_url
            self.build_path = self.source_path

        self.paths = {
            'full': os.path.join(self.site.path, 'pages', self.source_path),
            'full-build': os.path.join(site.paths['build'], self.build_path),
        }

    def is_html(self):
        return urlparse.urlparse(self.source_path).path.endswith('.html')

    def is_index(self):
        return urlparse.urlparse(self.source_path).path.endswith('index.html')

    @property
    def absolute_final_url(self):
        """
        Return the absolute URL for this page in the final build
        """
        return urlparse.urljoin(self.site.url, self.final_url)

    def data(self):
        f = codecs.open(self.paths['full'], 'r', 'utf-8')
        data = f.read()
        f.close()
        return data

    def context(self):
        """
        The page context.
        """
        # Site context, making a shallow-copy using dict so that the
        # things we add to this page's context below won't be added to
        # the site's context. if in the future we make non-top-level
        # changes to the page's context the shallow copy won't be
        # enough, we'd need to look at copy.deepcopy
        context = copy.copy(self.site.context())

        # Relative url context
        prefix = '/'.join(['..' for i in xrange(len(self.source_path.split('/')) - 1)]) or '.'

        context.update({
            'STATIC_URL': os.path.join(prefix, 'static'),
            'ROOT_URL': prefix,
            '__CACTUS_CURRENT_PAGE__': self,
        })

        # Page context (parse header)
        context.update(parseValues(self.data())[0])

        return Context(context)

    def render(self):
        """
        Takes the template data with contect and renders it to the final output file.
        """

        data = parseValues(self.data())[1]
        context = self.context()

        # Run the prebuild plugins, we can't use the standard method here because
        # plugins can chain-modify the context and data.
        for plugin in self.site._plugins:
            if hasattr(plugin, 'preBuildPage'):
                context, data = plugin.preBuildPage(self, context, data)

        return Template(data).render(context)

    def build(self):
        """
        Save the rendered output to the output file.
        """
        logging.info('Building {0} --> {1}'.format(self.source_path, self.final_url))

        data = self.render()

        # Make sure a folder for the output path exists
        try:
            os.makedirs(os.path.dirname(self.paths['full-build']))
        except OSError:
            pass

        # Write the data to the output file
        f = codecs.open(self.paths['full-build'], 'w', 'utf-8')
        f.write(data)
        f.close()

        # Run all plugins
        self.site.pluginMethod('postBuildPage', self)
