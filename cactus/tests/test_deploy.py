#coding:utf-8
from __future__ import unicode_literals

import os
import shutil
import tempfile
import hashlib
import unittest2 as unittest
import mock

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.config.router import ConfigRouter
from cactus.deployment.file import BaseFile
from cactus.plugin.builtin.cache import CacheDurationPlugin
from cactus.plugin.loader import ObjectsPluginLoader
from cactus.plugin.manager import PluginManager


class TestHeadersPlugin(object):
    """
    An utility plugin to retrieve a file's header.
    """
    def __init__(self):
        self.headers = None

    def preDeployFile(self, file):
        self.file = file


class TestFile(BaseFile):
    def remote_changed(self):
        return True

    def do_upload(self):
        pass

class TestDeploymentEngine(BaseDeploymentEngine):
    CredentialsManagerClass = lambda self, engine: None  # We never use it here


#TODO: Retest this with a custom deployment engine or file class

class TestDeployFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.build_path = os.path.join(self.test_dir, '.build')
        os.mkdir(self.build_path)


        self.site = mock.MagicMock()
        self.site.plugin_manager = PluginManager(self.site, [])
        self.site.path = self.test_dir
        self.site.build_path = self.build_path
        self.site.config = ConfigRouter([os.path.join(self.test_dir, "config.json")])
        self.site.config.set("site-url", "http://example.com")

        self.engine = TestDeploymentEngine(self.site)


    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_cache_control(self):
        """
        Ensure that the Cache control headers are properly set
        """
        # Test a fingerprinted file
        content = 'abc'
        h = hashlib.md5(content.encode('utf-8')).hexdigest()
        filename = "file.{0}.data".format(h)

        with open(os.path.join(self.build_path,  filename), "w") as f:
            f.write(content)

        p = TestHeadersPlugin()
        self.site.plugin_manager.loaders = [ObjectsPluginLoader([p, CacheDurationPlugin()])]
        self.site.plugin_manager.reload()
        self.site.plugin_manager.preDeploy(self.site)

        f = TestFile(self.engine, filename)
        f.upload()

        self.assertEqual(p.file.cache_control, f.MAX_CACHE_EXPIRATION)


        # Test a non fingerprinted file
        with open(os.path.join(self.build_path, "123.html"), "w") as f:
            f.write("abc")

        # Prepare setup
        p = TestHeadersPlugin()
        self.site.plugin_manager.loaders = [ObjectsPluginLoader([p, CacheDurationPlugin()])]
        self.site.plugin_manager.reload()
        f = TestFile(self.engine, "123.html")

        # Test with no configured cache duration
        self.site.config.set("cache-duration", None)
        self.site.plugin_manager.preDeploy(self.site)

        f.upload()
        self.assertEqual(p.file.cache_control, f.DEFAULT_CACHE_EXPIRATION)

        # Test with a configured cache duration
        self.site.config.set("cache-duration", 123)
        self.site.plugin_manager.preDeploy(self.site)

        f.upload()
        self.assertEqual(p.file.cache_control, 123)
