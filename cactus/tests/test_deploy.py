#coding:utf-8
import os
import shutil
import tempfile
import unittest
import mock
import hashlib
from cactus.config.router import ConfigRouter

from cactus.file import File
from cactus.plugin.loader import ObjectsPluginLoader
from cactus.plugin.manager import PluginManager


class TestHeadersPlugin(object):
    """
    An utility plugin to retrieve a file's header.
    """
    def __init__(self):
        self.headers = None

    def preDeployFile(self, file):
        self.headers = file.headers

@mock.patch("cactus.utils.url.getURLHeaders")
class TestDeployFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.build_path = os.path.join(self.test_dir, '.build')
        os.mkdir(self.build_path)

        self.site = mock.MagicMock()
        self.site.plugin_manager = PluginManager([])
        self.site.path = self.test_dir
        self.site.config = ConfigRouter([os.path.join(self.test_dir, "config.json")])
        self.site.config.set("site-url", "http://example.com")

        self.bucket = mock.MagicMock()


    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_cache_control(self, getURLHeadersMock):
        """
        Ensure that the Cache control headers are properly set
        """
        # Test a fingerprinted file
        content = 'abc'
        h = hashlib.md5(content).hexdigest()
        filename = "file.{0}.data".format(h)

        with open(os.path.join(self.build_path,  filename), "w") as f:
            f.write(content)

        p = TestHeadersPlugin()
        self.site.plugin_manager.loaders = [ObjectsPluginLoader([p])]
        self.site.plugin_manager.reload()
        f = File(self.site, filename)
        f.upload(self.bucket)

        self.assertIn("cache-control", p.headers)
        cache_control = p.headers["cache-control"]
        self.assertTrue(cache_control.startswith('max-age='))
        self.assertEqual(int(cache_control.split('=')[1]), f.MAX_CACHE_EXPIRATION)


        # Test a non fingerprinted file
        with open(os.path.join(self.build_path, "123.html"), "w") as f:
            f.write("abc")

        p = TestHeadersPlugin()
        self.site.plugin_manager.loaders = [ObjectsPluginLoader([p])]
        self.site.plugin_manager.reload()
        f = File(self.site, "123.html")

        self.site.config.set("cache-duration", None)
        f.upload(self.bucket)
        self.assertIn("cache-control", p.headers)
        cache_control = p.headers["cache-control"]
        self.assertTrue(cache_control.startswith('max-age='))
        self.assertEqual(int(cache_control.split('=')[1]), f.DEFAULT_CACHE_EXPIRATION)

        self.site.config.set("cache-duration", 123)
        f.upload(self.bucket)
        self.assertIn("cache-control", p.headers)
        cache_control = p.headers["cache-control"]
        self.assertTrue(cache_control.startswith('max-age='))
        self.assertEqual(int(cache_control.split('=')[1]), 123)

    def test_new_html(self, getURLHeadersMock):
        """
        Ensure that we deploy files
        """
        with open(os.path.join(self.build_path, "123.html"), "w") as f:
            f.write('abc')

        f = File(self.site, "123.html")
        f.upload(self.bucket)

        new_key = self.bucket.new_key.call_args
        self.assertNotEqual(new_key, None)  # Was this called?
        positional, keywords = new_key
        self.assertEqual(positional, ("123.html",))