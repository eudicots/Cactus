#coding:utf-8
import os
import shutil
import tempfile
import unittest
import mock
import collections

from cactus.file import File


class TestDeployFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.build_path = os.path.join(self.test_dir, '.build')
        os.mkdir(self.build_path)

        self.site = mock.MagicMock()
        self.site.cache_duration = 123
        self.site.path = self.test_dir
        self.site.config.get.return_value = "example.com"
        self.site.plugin_manager.preDeployFile.return_value = None

        bucket_type = collections.namedtuple("Bucket", "new_key set_contents_from_string")

        self.bucket = bucket_type(mock.MagicMock(), mock.MagicMock())

    def test_new_html(self):
        with open(os.path.join(self.build_path, "123.html"), "w") as f:
            f.write('abc')

        f = File(self.site, "123.html")
        f.upload(self.bucket)

        new_key = self.bucket.new_key.call_args
        self.assertNotEqual(new_key, None)  # Was this called?
        positional, keywords = new_key
        self.assertEqual(positional, ("123.html",))



    def tearDown(self):
        shutil.rmtree(self.test_dir)