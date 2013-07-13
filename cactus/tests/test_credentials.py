#coding:utf-8
import os
import shutil
import tempfile
import collections
from cactus.deployment.s3.auth import AWSCredentialsManager

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from cactus.config.file import ConfigFile


class DummySite(object):
    def __init__(self, config):
        self.config = config

class DummyPasswordManager(object):
    def __init__(self):
        self.passwords = collections.defaultdict(dict)

    def set_password(self, service, account, password):
        self.passwords[service][account] = password

    def get_password(self, service, account):
        try:
            return self.passwords[service][account]
        except KeyError:
            return None


class CredentialsManagerTestCase(unittest.TestCase):
    aws_access_key = "123"
    aws_secret_key = "123"

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, "conf1.json")
        self.config = ConfigFile(self.path)

        self.site = DummySite(self.config)
        self.password_manager = DummyPasswordManager()

        self.credentials_manager = AWSCredentialsManager(self.site, self.password_manager)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_config(self):
        """
        Test that credentials can be retrieved from the config
        """
        self.config.set("aws-access-key", self.aws_access_key)
        self.password_manager.set_password("aws", self.aws_access_key, self.aws_secret_key)

        credentials = self.credentials_manager.get_credentials()

        self.assertEqual(2, len(credentials))
        self.assertEqual(self.aws_access_key, credentials["access_key"])
        self.assertEqual(self.aws_secret_key, credentials["secret_key"])

    def test_write_config(self):
        """
        Test that credentials are persisted to a config file
        """
        self.credentials_manager.access_key = self.aws_access_key
        self.credentials_manager.secret_key = self.aws_secret_key
        self.credentials_manager.save_credentials()

        self.config.load()
        self.assertEqual(self.aws_access_key, self.config.get("aws-access-key"))

        self.assertEqual(self.aws_secret_key, self.password_manager.get_password("aws", "123"))
