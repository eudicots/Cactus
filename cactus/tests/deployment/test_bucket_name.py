#coding:utf-8
from cactus.tests.deployment import DummyUI, DummySite, DummyDeploymentEngine, BaseDeploymentTestCase


class BucketNameTestCase(BaseDeploymentTestCase):
    def setUp(self):
        super(BucketNameTestCase, self).setUp()
        self.ui = DummyUI(create_bucket=False)
        self.site = DummySite(self.test_dir, self.ui)
        self.engine = DummyDeploymentEngine(self.site)

    def test_not_configured(self):
        """
        Test that we prompt the bucket name in case it's not configured
        """
        self.assertEqual(0, self.ui.asked_name)

        self.engine.configure()

        self.assertEqual(1, self.ui.asked_name)
        self.assertEqual("test-bucket", self.engine.bucket_name)

    def test_configured(self):
        """
        Test that we don't prompt the bucket name in case it's configured
        """
        self.site.config.set("test-conf-entry", "test-bucket")

        self.assertEqual(0, self.ui.asked_name)

        self.engine.configure()

        self.assertEqual(0, self.ui.asked_name)
        self.assertEqual("test-bucket", self.engine.bucket_name)
