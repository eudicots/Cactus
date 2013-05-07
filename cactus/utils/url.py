import httplib
import urllib
import urlparse
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