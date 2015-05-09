#coding:utf-8
from cactus.tests.deployment import DummyUI, DummySite, DummyDeploymentEngine, BaseDeploymentTestCase


class BucketCreateTestCase(BaseDeploymentTestCase):
    def setUp(self):
        super(BucketCreateTestCase, self).setUp()
        self.ui = DummyUI()
        self.site = DummySite(self.test_dir, self.ui)
        self.engine = DummyDeploymentEngine(self.site)
        self.engine.configure()

    def test_bucket_attrs(self):
        """
        Test that the bucket name is provided
        """
        self.assertEqual("test-bucket", self.engine.bucket_name)
        self.assertEqual("test-bucket-obj", self.engine.bucket)

    def test_config_saved(self):
        """
        Test that the configuration is saved
        """
        self.assertEqual("test-bucket", self.site.config.get("test-conf-entry"))
        self.assertEqual("http://test-bucket.com", self.site.config.get("test-conf-entry-website"))

    def test_credentials_saved(self):
        """
        Test that the credentials are saved
        """
        self.assertTrue(self.engine.credentials_manager.saved)
