#coding:utf-8
import os
import logging


class PageContextCompatibilityPlugin(object):
    """
    This plugin ensures that the page context stays backwards compatible, but adds
    deprecation warnings.
    """
    def preBuildPage(self, page, context, data):
        prefix = '/'.join(['..' for i in xrange(len(page.source_path.split('/')) - 1)]) or '.'

        def static_url():
            logging.warn("{{ STATIC_URL }} is deprecated, use {% static '/static/path/to/file' %} instead.")
            return os.path.join(prefix, 'static')

        def root_url():
            logging.warn("{{ ROOT_URL }} is deprecated, use {% url '/page.html' %} instead.")
            return prefix

        def page_url():
            logging.warn("{{ PAGE_URL }} is deprecated, use {% current_page %} instead")
            return page.source_path

        context.update({
            "STATIC_URL": static_url,
            "ROOT_URL": root_url,
            "PAGE_URL": page_url,
        })

        return context, data