#coding:utf-8
from cactus.tests.integration.s3 import S3IntegrationTestCase


class BucketTestCase(S3IntegrationTestCase):
    def test_create_bucket(self):
        """
        Test that we properly create a bucket in AWS
        """
        self.site.deployment_engine.bucket_name = "new"
        bucket = self.site.deployment_engine.create_bucket()

        self.assertEqual("new", bucket.name)

        self.assertEqual(2, len(self.connection_factory.requests))
        new, configure = self.connection_factory.requests

        self.assertEqual("/", new.path)
        self.assertEqual("PUT", new.method)

        self.assertEqual("/?website", configure.url)
        self.assertEqual("PUT", configure.method)

        for req in (new, configure):
            self.assertEqual("new.s3.amazonaws.com", req.connection.host)

    def test_list_buckets(self):
        """
        Test that we retrieve the correct list of buckets from AWS
        """
        buckets = self.site.deployment_engine._get_buckets()
        bucket_names = [bucket.name for bucket in buckets]

        self.assertEqual(sorted(bucket_names), sorted(["website", "other"]))
        self.assertEqual(1, len(self.connection_factory.requests))
        req = self.connection_factory.requests[0]
        self.assertEqual("GET", req.method)
        self.assertEqual("/", req.path)

    def test_get_bucket(self):
        """
        Test that we access the correct bucket in AWS
        """
        self.site.deployment_engine.bucket_name = "other"
        bucket = self.site.deployment_engine.get_bucket()

        self.assertEqual("other", bucket.name)
        self.assertEqual(1, len(self.connection_factory.requests))
        req = self.connection_factory.requests[0]
        self.assertEqual("GET", req.method)
        self.assertEqual("/", req.path)
