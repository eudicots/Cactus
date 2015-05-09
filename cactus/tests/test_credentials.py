#coding:utf-8
import os
import shutil
import tempfile
import keyring
import keyring.backend
import unittest2 as unittest

from cactus.deployment.s3.auth import AWSCredentialsManager
from cactus.config.file import ConfigFile


class DummySite(object):
    def __init__(self, config):
        self.config = config


class DummyEngine(object):
    def __init__(self, site):
        self.site = site


class TestKeyring(keyring.backend.KeyringBackend):
    def __init__(self):
        self.password = ''

    def supported(self):
        return 0

    def get_password(self, service, username):
        return self.password

    def set_password(self, service, username, password):
        self.password = password
        return 0

    def delete_password(self, service, username):
        self.password = None


class CredentialsManagerTestCase(unittest.TestCase):
    aws_access_key = "123"
    aws_secret_key = "456"

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, "conf1.json")
        self.config = ConfigFile(self.path)

        self.site = DummySite(self.config)
        self.engine = DummyEngine(self.site)

        self._initial_keyring = keyring.get_keyring()
        self.keyring = TestKeyring()
        keyring.set_keyring(self.keyring)

        self.credentials_manager = AWSCredentialsManager(self.engine)

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        keyring.set_keyring(self._initial_keyring)

    def test_read_config(self):
        """
        Test that credentials can be retrieved from the config
        """
        self.config.set("aws-access-key", self.aws_access_key)
        self.keyring.set_password("aws", self.aws_access_key, self.aws_secret_key)

        credentials = self.credentials_manager.get_credentials()
        self.assertEqual(2, len(credentials))

        username, password = credentials
        self.assertEqual(self.aws_access_key, username)
        self.assertEqual(self.aws_secret_key, password)

    def test_write_config(self):
        """
        Test that credentials are persisted to a config file
        """
        self.credentials_manager.username = self.aws_access_key
        self.credentials_manager.password = self.aws_secret_key
        self.credentials_manager.save_credentials()

        self.config.load()

        self.assertEqual(self.aws_access_key, self.config.get("aws-access-key"))
        self.assertEqual(self.aws_secret_key, self.keyring.get_password("aws", "123"))
