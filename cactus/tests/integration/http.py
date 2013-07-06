#coding:utf-8
import httplib
import urlparse
from cactus.utils.helpers import CaseInsensitiveDict


class BaseTestHTTPConnection(object):
    last_request = None

    def __init__(self, host, *args, **kwargs):
        pass

    def connect(self):
        pass

    def close(self):
        pass

    def request(self, method, url, body='', headers=None):
        """
        Send a full request at once
        """
        if headers is None:
            headers = {}
        self.last_request = TestHTTPRequest(method, url, body, headers)

    def putrequest(self, method, url, *args, **kwargs):
        """
        Create a new request, but add more things to it later
        """
        self.current_request = TestHTTPRequest(method, url, '', {})
        self.current_request.state = "headers"

    def putheader(self, header, value):
        """
        Add an header to a request that's in progress
        """
        self.current_request.headers[header] = value

    def endheaders(self, data=None):
        """
        End the headers of a request that's in progress
        """
        self.current_request.state = "body"
        self.last_request = self.current_request

        if data is not None:
            self.send(data)

    def send(self, data):
        """
        Add data to a request that's in progress
        """
        self.current_request.body += data

    def getresponse(self):
        raise NotImplementedError("You must subclass BaseTestHTTPConnection")

    def set_debuglevel(self, level):
        pass


class DebugHTTPSConnectionFactory(object):
    def __init__(self, conn_cls):
        self.conn_cls = conn_cls
        self.connections = []

    def __call__(self, *args, **kwargs):
        """
        Create a new connection from our connection class
        """
        connection = self.conn_cls(*args, **kwargs)
        self.connections.append(connection)
        return connection


class TestHTTPRequest(object):
    state = None

    def __init__(self, method, url, body, headers):
        self.method = method
        self.url = url
        self.body = body
        self.headers = CaseInsensitiveDict(headers)

        u = urlparse.urlparse(url)
        self.path = u.path
        self.params = urlparse.parse_qs(u.query, keep_blank_values=True)


class TestHTTPResponse(object):
    def __init__(self, status, reason=None, headers=None, body=''):
        if reason is None:
            reason = httplib.responses[status]
        if headers is None:
            headers = {}

        self.status = status
        self.reason = reason
        self.headers = CaseInsensitiveDict(headers)
        self.body = body

    def getheader(self, header, default=None):
        return self.headers.get(header, default)

    def getheaders(self):
        return self.headers

    def read(self):
        return self.body