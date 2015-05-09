#coding:utf-8
import os
import re

from cactus.deployment.s3.engine import S3DeploymentEngine
from cactus.utils.helpers import checksum

from cactus.tests.integration import IntegrationTestCase, DebugHTTPSConnectionFactory, BaseTestHTTPConnection, \
    TestHTTPResponse


class DummyAWSCredentialsManager(object):
    def __init__(self, site):
        self.site = site

    def get_credentials(self):
        return "123", "abc"

    def save_credentials(self):
        pass


class S3TestHTTPConnection(BaseTestHTTPConnection):

    def handle_request(self, request):
        if request.method == "GET":
            # List buckets
            if request.path == "/":
                if request.params == {}:
                    return self.list_buckets()
            # Request for just one bucket (like /bucket/ - regex is not perfect but should do for here)
            if re.match(r"/[a-z1-9\-.]+/", request.path):
                if "location" in request.params:
                    return self.location()

        if request.method == "PUT":
            if request.path == "/":
                return TestHTTPResponse(200)
            return self.put_object(request)

        raise Exception("Unsupported request {0} {1}".format(request.method, request.url))

    def _serve_data(self, name):
        with open(os.path.join("cactus/tests/integration/s3/data", name)) as f:
            return TestHTTPResponse(200, body=f.read())

    def list_buckets(self):
        return self._serve_data("buckets.xml")

    def location(self):
        return self._serve_data("location.xml")

    def put_object(self, req):
        return TestHTTPResponse(200, headers={"ETag":'"{0}"'.format(checksum(req.body))})


class S3IntegrationTestCase(IntegrationTestCase):
    def get_deployment_engine_class(self):
        # Create a connection factory
        self.connection_factory = DebugHTTPSConnectionFactory(S3TestHTTPConnection)

        class TestS3DeploymentEngine(S3DeploymentEngine):
            _s3_https_connection_factory = (self.connection_factory, ())
            CredentialsManagerClass = DummyAWSCredentialsManager

        return TestS3DeploymentEngine

    def get_credentials_manager_class(self):
        return DummyAWSCredentialsManager
