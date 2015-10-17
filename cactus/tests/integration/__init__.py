#coding:utf-8
from __future__ import unicode_literals

import os
import shutil
from six.moves import http_client, urllib

from cactus.site import Site
from cactus.plugin.manager import PluginManager
from cactus.utils.helpers import CaseInsensitiveDict
from cactus.utils.parallel import PARALLEL_DISABLED

from cactus.tests import BaseBootstrappedTestCase


class DummyPluginManager(PluginManager):
    """
    Doesn't do anything
    """
    def call(self, method, *args, **kwargs):
        """
        Trap the call
        """
        pass


class IntegrationTestCase(BaseBootstrappedTestCase):
    def setUp(self):
        super(IntegrationTestCase, self).setUp()

        self.site = Site(self.path,
            PluginManagerClass=DummyPluginManager, DeploymentEngineClass=self.get_deployment_engine_class())
        self.site._parallel = PARALLEL_DISABLED

        self.site.config.set('site-url', 'http://example.com/')

        # Clean up the site paths
        for path in (self.site.page_path, self.site.static_path):
            shutil.rmtree(path)
            os.mkdir(path)

    def get_deployment_engine_class(self):
        """
        Should return a deployment engine in tests.
        """
        pass


class BaseTestHTTPConnection(object):
    last_request = None

    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.requests = []

    def connect(self):
        pass

    def close(self):
        pass

    def request(self, method, url, body=b'', headers=None):
        """
        Send a full request at once
        """
        if headers is None:
            headers = {}
        self.last_request = TestHTTPRequest(self, method, url, body, headers)

    def putrequest(self, method, url, *args, **kwargs):
        """
        Create a new request, but add more things to it later
        """
        self.current_request = TestHTTPRequest(self, method, url, b'', {})
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
        request = self.last_request
        self.requests.append(request)
        return self.handle_request(request)

    def handle_request(self, request):
        """
        :param request: The request to handle
        """
        raise NotImplementedError("handle_request should be implemented by subclasses")


    def set_debuglevel(self, level):
        pass


class DebugHTTPSConnectionFactory(object):
    def __init__(self, conn_cls):
        self.conn_cls = conn_cls
        self.connections = []

    @property
    def requests(self):
        """
        :returns: A dictionary of the calls made through this connection factory (method -> list of calls)
        """
        out = []
        for connection in self.connections:
            out.extend(connection.requests)
        return out

    def __call__(self, *args, **kwargs):
        """
        Create a new connection from our connection class
        """
        connection = self.conn_cls(*args, **kwargs)
        self.connections.append(connection)
        return connection


class TestHTTPRequest(object):
    state = None

    def __init__(self, connection, method, url, body, headers):
        self.connection = connection

        self.method = method
        self.url = url
        self.body = body
        self.headers = CaseInsensitiveDict(headers)

        u = urllib.parse.urlparse(url)
        self.path = u.path
        self.params = urllib.parse.parse_qs(u.query, keep_blank_values=True)


class TestHTTPResponse(object):
    def __init__(self, status, reason=None, headers=None, body=''):
        if reason is None:
            reason = http_client.responses[status]
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
