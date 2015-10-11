# Python 3.5 Django compatibility fix:
# + https://github.com/django/django/commit/b07aa52e8a8e4c7fdc7265f75ce2e7992e657ae9)
# + https://code.djangoproject.com/ticket/23763
import six

if six.PY3:
    import html.parser as _html_parser

    try:
        HTMLParseError = _html_parser.HTMLParseError
    except AttributeError:
        # create a dummy class for Python 3.5+ where it's been removed
        class HTMLParseError(Exception):
            pass

        _html_parser.HTMLParseError = HTMLParseError

