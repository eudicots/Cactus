#coding:utf-8
import os

from cactus.tests.integration.http import BaseTestHTTPConnection, TestHTTPResponse
from cactus.utils.helpers import checksum


class S3TestHTTPConnection(BaseTestHTTPConnection):

    def handle_request(self, request):
        if request.method == "GET":
            if request.path == "/":
                if request.params == {}:
                    return self.list_buckets()
                if "location" in request.params:
                    return self.location()

        if request.method == "PUT":
            if request.path == "/":
                return TestHTTPResponse(200)
            return self.put_object(request)

        raise Exception("Unsupported request {0} {1}".format(request.method, request.url))

    def _serve_data(self, name):
        with open(os.path.join("cactus/tests/integration/data", name)) as f:
            return TestHTTPResponse(200, body=f.read())

    def list_buckets(self):
        return self._serve_data("buckets.xml")

    def location(self):
        return self._serve_data("location.xml")

    def put_object(self, req):
        return TestHTTPResponse(200, headers={"ETag":'"{0}"'.format(checksum(req.body))})