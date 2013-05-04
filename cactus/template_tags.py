#coding:utf-8
from django.template.base import Library

register = Library()


def static(context, link_path):
    """
    Get the path for a static file in the Cactus build.
    We'll need this because paths are rewritten with fingerprinting.
    """
    return context['__CACTUS_SITE__'].get_path_for_static(link_path)


def url(context, link_path):
    """
    Get the path for a page in the Cactus build.
    We'll need this because paths are rewritten with fingerprinting.
    """
    site = context['__CACTUS_SITE__']
    url = site.get_path_for_page(link_path)

    if site.prettify_urls:
        return url.rsplit('index.html', 1)[0]

    return url


def if_current_page(context, link_path, positive=True, negative=False):
    """
    Return one of the passed parameters if the URL passed is the current one.
    For consistency reasons, we use the link_path of the page.
    """
    current_page = context['__CACTUS_CURRENT_PAGE__']

    return positive if current_page.link_path == link_path else negative


register.simple_tag(takes_context=True)(static)
register.simple_tag(takes_context=True)(url)
register.simple_tag(takes_context=True)(if_current_page)