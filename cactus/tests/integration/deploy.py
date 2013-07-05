#coding:utf-8
import os
import StringIO
import gzip

from cactus.tests.integration import IntegrationTestCase
from cactus.tests.integration.http import BaseTestHTTPConnection, TestHTTPResponse
from cactus.utils.helpers import checksum


class TestHTTPConnection(BaseTestHTTPConnection):

    def __init__(self, *args, **kwargs):
        super(TestHTTPConnection, self).__init__(*args, **kwargs)

        self.calls = {
            "bucket_list": 0,
            "location": 0,
            "put": [],
        }

    def getresponse(self):
        req = self.last_request

        if req.method == "GET":
            if req.path == "/":
                if req.params == {}:
                    return self.list_buckets()
                if "location" in req.params:
                    return self.location()

        if req.method == "PUT":
            return self.put_object(req)

        raise Exception("Unsupported request {0} {1}".format(req.method, req.url))

    def _serve_data(self, name):
        with open(os.path.join("cactus/tests/integration/data", name)) as f:
            return TestHTTPResponse(200, body=f.read())

    def list_buckets(self):
        self.calls["bucket_list"] += 1
        return self._serve_data("buckets.xml")

    def location(self):
        self.calls["location"] += 1
        return self._serve_data("location.xml")

    def put_object(self, req):
        self.calls["put"].append(req)
        return TestHTTPResponse(200, headers={"ETag":'"{0}"'.format(checksum(req.body))})



class DeployTestCase(IntegrationTestCase):
    connection_class = TestHTTPConnection

    def test_simple_deploy(self):
        """
        Test our file deployment

        - Uploaded
        - Have the correct name
        - Compressed (if useful) -- #TODO
        - Publicly readable
        """

        payload = "\x01" * 1000 + "\x02" * 1000  # Will compress very well

        with open(os.path.join(self.site.static_path, "static.css"), 'wb') as f:
            f.write(payload)

        self.site.upload()

        connections = self.connection_factory.connections

        for connection in connections:
            # Check that we put our file
            if connection.calls["put"]:
                # How many files did we upload?
                self.assertEqual(1, len(connection.calls["put"]))

                # What file did we upload?
                put = connection.calls["put"][0]
                self.assertEqual(put.url, "/static/static.css")

                # Where the AWS standard headers correct?
                self.assertEqual(put.headers["x-amz-acl"], "public-read")
                self.assertEqual(put.headers["content-encoding"], "gzip")

                # Are the file contents correct?
                compressed = gzip.GzipFile(fileobj=StringIO.StringIO(put.body), mode="r")
                self.assertEqual(payload, compressed.read())
                break
        else:
            self.fail("No PUT call was found")
