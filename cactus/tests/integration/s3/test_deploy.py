#coding:utf-8
from __future__ import unicode_literals

import os
import io
import gzip

from six import BytesIO

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
        bucket_name = self.site.config.get("aws-bucket-name")

        payload = "\x01" * 1000 + "\x02" * 1000  # Will compress very well
        payload = payload.encode('utf-8')

        with io.FileIO(os.path.join(self.site.static_path, "static.css"), 'w') as f:
            f.write(payload)

        self.site.upload()

        puts = [req for req in self.connection_factory.requests if req.method == "PUT"]

        # How many files did we upload?
        self.assertEqual(1, len(puts))
        put = puts[0]

        # What file did we upload?
        self.assertEqual("/{0}/static/static.css".format(bucket_name), put.url)

        # Where the AWS standard headers correct?
        self.assertEqual("public-read", put.headers["x-amz-acl"])
        self.assertEqual("gzip", put.headers["content-encoding"])
        self.assertEqual("max-age={0}".format(BaseFile.DEFAULT_CACHE_EXPIRATION), put.headers["cache-control"])
        # We just have to check that the max age is set. Another test (test_deploy) checks that this value can be
        # changed using plugins

        # Did we use the correct access key?
        self.assertEqual("AWS 123", put.headers["authorization"].split(':')[0])

        # Did we talk to the right host?
        self.assertEqual("s3.amazonaws.com", put.connection.host)

        # Are the file contents correct?
        compressed = gzip.GzipFile(fileobj=BytesIO(put.body), mode="r")
        self.assertEqual(payload, compressed.read())

    def test_compression(self):
        compress_extensions = ["yes", "html"]
        payload = "\x01" * 1000 + "\x02" * 1000  # Will compress very well
        payload = payload.encode('utf-8')

        self.site.compress_extensions = compress_extensions

        with io.FileIO(os.path.join(self.site.static_path, "static.yes"), 'wb') as f:
            f.write(payload)

        with io.FileIO(os.path.join(self.site.static_path, "static.no"), 'wb') as f:
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
