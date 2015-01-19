#coding:utf-8
import os
import logging

from cactus.utils.url import path_to_url


logger = logging.getLogger(__name__)


class PageContextCompatibilityPlugin(object):
    """
    This plugin ensures that the page context stays backwards compatible, but adds
    deprecation warnings.
    """
    def preBuildPage(self, page, context, data):
        prefix = os.path.relpath(".", os.path.dirname(page.build_path))

        def static_url():
            logger.warn("%s:", page.path)
            logger.warn("{{ STATIC_URL }} is deprecated, use {% static '/static/path/to/file' %} instead.")
            return path_to_url(os.path.join(prefix, 'static'))

        def root_url():
            logger.warn("%s:", page.path)
            logger.warn("{{ ROOT_URL }} is deprecated, use {% url '/page.html' %} instead.")
            return path_to_url(prefix)

        def page_url():
            logger.warn("%s:", page.path)
            logger.warn("{{ PAGE_URL }} is deprecated, use {% current_page %} instead")
            return page.final_url[1:]  # We don't want the leading slash (backwards compatibility)

        context.update({
            "STATIC_URL": static_url,
            "ROOT_URL": root_url,
            "PAGE_URL": page_url,
        })

        return context, data
