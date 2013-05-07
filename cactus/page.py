import os
import codecs
import logging
import copy
import urlparse

from django.template import Template, Context


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
        with open(os.path.join(self.site.path, 'pages', self.source_path)) as f:
            return f.read().decode('utf-8')

    def context(self, extra=None):
        """
        The page context.
        """
        # Site context, making a shallow-copy using dict so that the
        # things we add to this page's context below won't be added to
        # the site's context. if in the future we make non-top-level
        # changes to the page's context the shallow copy won't be
        # enough, we'd need to look at copy.deepcopy
        context = copy.copy(self.site.context())

        context.update({
            '__CACTUS_CURRENT_PAGE__': self,
        })

        if extra is None:
            extra = {}
        context.update(extra)

        return Context(context)

    def render(self):
        """
        Takes the template data with context and renders it to the final output file.
        """

        page_context, data = self.parse_context(self.data())
        context = self.context(page_context)

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

        output_path = os.path.join(self.site.build_path, self.build_path)

        # Make sure a folder for the output path exists
        try:
            os.makedirs(os.path.dirname(output_path))
        except OSError:
            pass

        with open(output_path, 'w') as f:
            f.write(data.encode('utf-8'))

        # Run all plugins
        self.site.pluginMethod('postBuildPage', self)

    def parse_context(self, data, splitChar=':'):
        """
        Values like

        name: koen
        age: 29

        will be converted in a dict: {'name': 'koen', 'age': '29'}
        """

        if not self.is_html():
            return {}, data

        values = {}
        lines = data.splitlines()
        if not lines:
            return {}, ''

        for i, line in enumerate(lines):

            if not line:
                continue

            elif splitChar in line:
                line = line.split(splitChar)
                values[line[0].strip()] = (splitChar.join(line[1:])).strip()

            else:
                break

        return values, '\n'.join(lines[i:])

    def __repr__(self):
        return '<Page: {0}>'.format(self.source_path)
