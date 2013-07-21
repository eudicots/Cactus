#coding:utf-8
from cactus.tests.deployment import DummyUI, DummySite, DummyDeploymentEngine, BaseDeploymentTestCase


class BucketCreateTestCase(BaseDeploymentTestCase):
    def setUp(self):
        super(BucketCreateTestCase, self).setUp()
        self.ui = DummyUI()
        self.site = DummySite(self.test_dir, self.ui)
        self.engine = DummyDeploymentEngine(self.site)

    def test_bucket_does_not_exist(self):
        """
        Test that we create buckets that don't exist
        """
        self.assertEqual(0, self.engine.create_bucket_calls)
        self.assertEqual(0, self.ui.asked_create)

        self.engine.configure()

        self.assertEqual(1, self.engine.get_bucket_calls)
        self.assertEqual(1, self.engine.create_bucket_calls)
        self.assertEqual(1, self.ui.asked_create)

    def test_bucket_exists(self):
        """
        Test that we don't attempt to re-create buckets that exist
        """
        self.engine.create_bucket_calls = 1

        self.engine.configure()

        self.assertEqual(1, self.engine.create_bucket_calls)
        self.assertEqual(1, self.engine.get_bucket_calls)
        self.assertEqual(0, self.ui.asked_create)
