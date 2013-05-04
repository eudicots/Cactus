#coding:utf-8
from django.template.base import Library

register = Library()


def static(context, src_path):
    """
    Get the path for a static file in the Cactus build.
    We'll need this because paths are rewritten with fingerprinting.
    """
    return context['__CACTUS_SITE__'].get_path_for_static(src_path)


def url(context, src_path):
    """
    Get the path for a page in the Cactus build.
    We'll need this because paths are rewritten with fingerprinting.
    """
    site = context['__CACTUS_SITE__']
    url = site.get_path_for_page(src_path)

    if site.prettify_urls:
        return url.rsplit('index.html', 1)[0]

    return url


register.simple_tag(takes_context=True)(static)
register.simple_tag(takes_context=True)(url)