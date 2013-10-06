#coding:utf-8
import os
import StringIO
import gzip
from cactus.deployment.file import BaseFile

from cactus.tests.integration.s3 import S3IntegrationTestCase


class DeployTestCase(S3IntegrationTestCase):
    def setUp(self):
        super(DeployTestCase, self).setUp()
        self.site.config.set('aws-bucket-name', 'website')

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

        puts = [req for req in self.connection_factory.requests if req.method == "PUT"]

        # How many files did we upload?
        self.assertEqual(1, len(puts))
        put = puts[0]

        # What file did we upload?
        self.assertEqual("/static/static.css", put.url)

        # Where the AWS standard headers correct?
        self.assertEqual("public-read", put.headers["x-amz-acl"])
        self.assertEqual("gzip", put.headers["content-encoding"])
        self.assertEqual("max-age={0}".format(BaseFile.DEFAULT_CACHE_EXPIRATION), put.headers["cache-control"])
        # We just have to check that the max age is set. Another test (test_deploy) checks that this value can be
        # changed using plugins

        # Did we use the correct access key?
        self.assertEqual("AWS 123", put.headers["authorization"].split(':')[0])

        # Did we talk to the right host?
        self.assertEqual("website.s3.amazonaws.com", put.connection.host)

        # Are the file contents correct?
        compressed = gzip.GzipFile(fileobj=StringIO.StringIO(put.body), mode="r")
        self.assertEqual(payload, compressed.read())

    def test_compression(self):
        compress_extensions = ["yes", "html"]
        payload = "\x01" * 1000 + "\x02" * 1000  # Will compress very well
        self.site.compress_extensions = compress_extensions

        with open(os.path.join(self.site.static_path, "static.yes"), 'wb') as f:
            f.write(payload)

        with open(os.path.join(self.site.static_path, "static.no"), 'wb') as f:
            f.write(payload)

        self.site.upload()

        puts = [req for req in self.connection_factory.requests if req.method == "PUT"]

        self.assertEqual(2, len(puts))
        compressed = 0
        for put in puts:
            if put.url.rsplit(".", 1)[1] in compress_extensions:
                self.assertEqual("gzip", put.headers["content-encoding"])
                compressed += 1
            else:
                self.assertIsNone(put.headers.get("content-encoding"))

        self.assertEqual(1, compressed)
