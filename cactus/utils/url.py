import httplib
import urllib
import urlparse
import os

from cactus.utils.helpers import CaseInsensitiveDict


EXTERNAL_SCHEMES = ("//", "http://", "https://", "mailto:")


def getURLHeaders(url):
    url = urlparse.urlparse(url)

    conn = httplib.HTTPConnection(url.netloc)
    conn.request('HEAD', urllib.quote(url.path))

    response = conn.getresponse()

    return CaseInsensitiveDict(response.getheaders())


def is_external(url):
    for scheme in EXTERNAL_SCHEMES:
        if url.startswith(scheme):
            return True
    return False


def path_to_url(path):
    """
    Convert a system path to an URL
    """
    return path.replace(os.sep, "/")


def URLHelperMixinFactory(class_name, property_name):

    inner_property_name = "_" + property_name

    def setter(self, value):
        setattr(self, inner_property_name, value)

    def getter(self):
        return path_to_url(getattr(self, inner_property_name))

    def deleter(self):
        delattr(self, inner_property_name)

    return type(class_name, (object,), {
        property_name: property(getter, setter, deleter)
    })


class ResourceURLHelperMixin(
    URLHelperMixinFactory("LinkURLHelperMixin", "link_url"),
    URLHelperMixinFactory("FinalURLHelperMixin", "final_url")
):
    """
    This helper lets us set the `link_url` and `final_url` for our resources and ensure that we get compliant URLS on
    all systems, including Windows where os.path is not a POSIX path.
    """