#coding:utf-8
from cactus.tests.integration.s3 import S3TestHTTPConnection, S3IntegrationTestCase


class WorkflowTestCase(S3IntegrationTestCase):
    HTTPConnectionClass = S3TestHTTPConnection

    def test_bucket_name_unset(self):
        """
        Test that we prompt the user for the name of the bucket
        """
        self.assertEqual(None, self.site.config.get('aws-bucket-name'))
        self.assertEqual(None, self.site.config.get('aws-bucket-website'))

        bucket_name = "website"  # Need to pick a name that is in our XML list!

        self.site.ui.prompt_normalized = lambda q: bucket_name
        self.site.upload()

        self.assertEqual(bucket_name, self.site.config.get('aws-bucket-name'))
        self.assertEqual("{0}.s3-website-us-east-1.amazonaws.com".format(bucket_name),
            self.site.config.get('aws-bucket-website'))  # See the response we send (US standard).

    def test_no_bucket_create(self):
        """
        Test that we prompt for bucket creation if the bucket does not exist
        """
        bucket_name = "does-not-exist"

        self.site.config.set('aws-bucket-name', bucket_name)
        self.assertEqual(None, self.site.config.get('aws-bucket-website'))

        self.site.ui.prompt_yes_no = lambda q: True
        self.site.upload()

        # Check that we retrieved the list and created a bucket
        self.assertEqual(4, len(self.connection_factory.requests))
        list_buckets, create_bucket, enable_website, retrieve_location = self.connection_factory.requests

        self.assertEqual("/", list_buckets.url)
        self.assertEqual("GET", list_buckets.method)

        self.assertEqual("/{0}/".format(bucket_name), create_bucket.url)
        self.assertEqual("s3.amazonaws.com".format(bucket_name), create_bucket.connection.host)
        self.assertEqual("PUT", create_bucket.method)

        self.assertEqual("/{0}/?website".format(bucket_name), enable_website.url)
        self.assertEqual("PUT", enable_website.method)

        self.assertEqual("/{0}/?location".format(bucket_name), retrieve_location.url)
        self.assertEqual("GET", retrieve_location.method)

        # Check that we updated our config
        self.assertEqual("{0}.s3-website-us-east-1.amazonaws.com".format(bucket_name),
            self.site.config.get('aws-bucket-website'))  # See the response we send (US standard).

    def test_credentials_manager(self):
        """
        Test that credentials are saved in the manager
        """
        class DummyCredentialsManager(object):
            saved = False

            def get_credentials(self):
                return {"access_key": '123', "secret_key": '456'}

            def save_credentials(self):
                self.saved = True

        self.site.deployment_engine.credentials_manager = DummyCredentialsManager()
        self.site.config.set('aws-bucket-name', 'website')
        self.site.upload()

        self.assertTrue(self.site.deployment_engine.credentials_manager.saved)
