#coding:utf-8
from django.template.base import Library

register = Library()


def static(context, src_path):
    """
    Get the path for a static file in the Cactus build.
    We'll need this because paths are rewritten with fingerprinting.
    """
    return context['__CACTUS_SITE__'].get_path_for_static(src_path)


register.simple_tag(takes_context = True)(static)
