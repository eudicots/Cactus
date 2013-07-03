#coding:utf-8
from django.template.base import Library

register = Library()


def static(context, link_url):
    """
    Get the path for a static file in the Cactus build.
    We'll need this because paths can be rewritten with fingerprinting.
    """
    #TODO: Support URLS that don't start with `/static/`
    return context['__CACTUS_SITE__'].get_url_for_static(link_url)


def url(context, link_url):
    """
    Get the path for a page in the Cactus build.
    We'll need this because paths can be rewritten with prettifying.
    """
    site = context['__CACTUS_SITE__']
    url = site.get_url_for_page(link_url)

    if site.prettify_urls:
        return url.rsplit('index.html', 1)[0]

    return url


def current_page(context):
    """
    Returns the current URL
    """
    page = context['__CACTUS_CURRENT_PAGE__']

    return page.final_url


def if_current_page(context, link_url, positive=True, negative=False):
    """
    Return one of the passed parameters if the URL passed is the current one.
    For consistency reasons, we use the link_url of the page.
    """
    page = context['__CACTUS_CURRENT_PAGE__']

    return positive if page.link_url == link_url else negative


register.simple_tag(takes_context=True)(static)
register.simple_tag(takes_context=True)(url)
register.simple_tag(takes_context=True)(current_page)
register.simple_tag(takes_context=True)(if_current_page)