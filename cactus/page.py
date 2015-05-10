import os
import logging
import urlparse

from django.template import Template, Context
from cactus.compat.paths import PageCompatibilityLayer
from cactus.utils.url import ResourceURLHelperMixin
from cactus.utils.helpers import memoize


logger = logging.getLogger(__name__)


class Page(PageCompatibilityLayer, ResourceURLHelperMixin):
    
    discarded = False

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

    @property
    def full_source_path(self):
        return os.path.join(self.site.path, 'pages', self.source_path)

    @property
    def full_build_path(self):
        return os.path.join(self.site.build_path, self.build_path)

    def data(self):
        with open(self.full_source_path, 'rU') as f:
            try:
                return f.read().decode('utf-8')
            except:
                logger.warning("Template engine could not process page: %s", self.path)

    def context(self):
        """
        The page context.
        """
        context = {'__CACTUS_CURRENT_PAGE__': self,}
        context.update(self.site.context())
        return Context(context)

    def render(self):
        """
        Takes the template data with context and renders it to the final output file.
        """

        context, data = self.site.plugin_manager.preBuildPage(
            self.site, self, self.context(), self.data())

        return Template(data).render(context)

    def build(self):
        """
        Save the rendered output to the output file.
        """
        logger.debug('Building {0} --> {1}'.format(self.source_path, self.final_url))  #TODO: Fix inconsistency w/ static
        data = self.render()  #TODO: This calls preBuild indirectly. Not great.

        if not self.discarded:

            # Make sure a folder for the output path exists
            try:
                os.makedirs(os.path.dirname(self.full_build_path))
            except OSError:
                pass

            with open(self.full_build_path, 'w') as f:
                f.write(data.encode('utf-8'))

            self.site.plugin_manager.postBuildPage(self)

    def __repr__(self):
        return '<Page: {0}>'.format(self.source_path)
