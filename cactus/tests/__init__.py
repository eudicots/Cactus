#coding:utf-8
import os
import tempfile
import shutil
import unittest2 as unittest

import django.conf

from cactus.site import Site
from cactus.bootstrap import bootstrap
from cactus.config.router import ConfigRouter
from cactus.utils.parallel import PARALLEL_DISABLED


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, 'test')
        self.clear_django_settings()

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
            path_dir = os.path.dirname(path)
            msg = [
                "File does not exist: {0}".format(path),
                "The following files *did* exist in {0}: {1}".format(path_dir, os.listdir(path_dir))
            ]
            self.fail("\n".join(msg))

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


class BaseBootstrappedTestCase(BaseTestCase):
    def setUp(self):
        super(BaseBootstrappedTestCase, self).setUp()
        bootstrap(self.path, os.path.join("cactus", "tests", "data", "skeleton"))


class SiteTestCase(BaseBootstrappedTestCase):
    def setUp(self):
        super(SiteTestCase, self).setUp()
        self.config_path = os.path.join(self.path, 'config.json')
        self.conf = ConfigRouter([self.config_path])
        self.conf.set('site-url', 'http://example.com/')
        for k, v in self.get_config_for_test().items():
            self.conf.set(k, v)
        self.conf.write()

        self.site = Site(self.path, [self.config_path])
        self.site._parallel = PARALLEL_DISABLED

    def get_config_for_test(self):
        """
        Hook to set config keys in other tests.
        """
        return {}
