#coding:utf-8
import unittest
import tempfile
import shutil
import os

import django.conf

from cactus.utils.packaging import bootstrap
from cactus import Site
from cactus.config.router import ConfigRouter



class BaseTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, 'test')
        self.clear_django_settings()

        bootstrap(self.path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def clear_django_settings(self):
        django.conf.settings._wrapped = django.conf.empty

    def assertFileExists(self, path):
        """
        Check that a file at path exists.
        """
        try:
            open(path)
        except IOError:
            self.fail("File does not exist: {0}".format(path))

    def assertFileDoesNotExist(self, path):
        """
        Check that the file at path does not exist.
        """
        try:
            open(path)
        except IOError:
            pass
        else:
            self.fail("File exists: {0}".format(path))



class SiteTest(BaseTest):
    def setUp(self):
        super(SiteTest, self).setUp()
        self.config_path = os.path.join(self.path, 'config.json')
        self.conf = ConfigRouter([self.config_path])
        self.conf.set('site-url', 'http://example.com/')
        for k, v in self.get_config_for_test().items():
            self.conf.set(k, v)
        self.conf.write()

        self.site = Site(self.path, [self.config_path], self.get_variables_for_test())

    def get_config_for_test(self):
        """
        Hook to set config keys in other tests.
        """
        return {}

    def get_variables_for_test(self):
        """
        Hook to set site variables in other tests
        """
        return []