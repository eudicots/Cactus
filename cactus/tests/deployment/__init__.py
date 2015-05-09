#coding:utf-8
import shutil
import tempfile
import unittest2 as unittest

from cactus.plugin.manager import PluginManager
from cactus.utils.parallel import PARALLEL_DISABLED
from cactus.config.fallback import ConfigFallback
from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.file import BaseFile


class DummyUI(object):
    """
    A class to mock the site's UI and have it return what we need
    """
    def __init__(self, bucket_name="test-bucket", create_bucket=True):
        self.bucket_name = bucket_name
        self.create_bucket = create_bucket

        self.asked_name = 0
        self.asked_create = 0

    def prompt_normalized(self, q):
        self.asked_name +=1
        return self.bucket_name

    def prompt_yes_no(self, q):
        self.asked_create += 1
        return self.create_bucket


class DummyConfig(ConfigFallback):
    """
    A ConfigFallback that remembers whether we saved
    """
    def write(self):
        super(DummyConfig, self).write()
        self.saved = True


class DummyPluginManager(PluginManager):
    """
    Doesn't do anything
    """
    def call(self, method, *args, **kwargs):
        """
        Trap the call
        """
        pass


class DummySite(object):
    """
    Something that pretends to be a site, as far as the deployment engine knows
    """
    _parallel = PARALLEL_DISABLED

    def __init__(self, path, ui):
        self.build_path = path
        self.config = ConfigFallback()
        self.ui = ui
        self.plugin_manager = DummyPluginManager(self, [])
        self.compress_extensions = []


class DummyCredentialsManager(object):
    """
    Something that looks like a CredentialsManager, as far as we know.
    """
    _username = "123"
    _password = "456"

    def __init__(self, engine):
        self.engine = engine
        self.saved = False

    def get_credentials(self):
        return self._username, self ._password

    def save_credentials(self):
        self.saved = True


class DummyFile(BaseFile):
    """
    A fake file class we can extend to test things
    """
    def __init__(self, engine, path):
        super(DummyFile, self).__init__(engine, path)
        self.engine.created_files.append(self)
        self.remote_changed_calls = 0
        self.do_upload_calls = 0

    def remote_changed(self):
        self.remote_changed_calls += 1
        return True

    def do_upload(self):
        self.do_upload_calls += 1
        pass


class DummyDeploymentEngine(BaseDeploymentEngine):
    """
    A deployment engine we can extend
    """
    FileClass = DummyFile
    CredentialsManagerClass = DummyCredentialsManager

    config_bucket_name = "test-conf-entry"
    config_bucket_website = "test-conf-entry-website"

    def __init__(self, site):
        super(DummyDeploymentEngine, self).__init__(site)
        self.get_bucket_calls = 0
        self.create_bucket_calls = 0
        self.get_website_calls = 0
        self.created_files = []

    def _create_connection(self):
        pass

    def get_bucket(self):
        self.get_bucket_calls += 1
        if self.create_bucket_calls:
            return "test-bucket-obj"
        return None

    def create_bucket(self):
        self.create_bucket_calls += 1
        return "test-bucket-obj"

    def get_website_endpoint(self):
        self.get_website_calls += 1
        return "http://test-bucket.com"


class BaseDeploymentTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
