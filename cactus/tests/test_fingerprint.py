#coding:utf-8
import os
from cactus import Site
from cactus.config import Config
from cactus.tests import BaseTest


class TestFingerprinting(BaseTest):
    def initialize(self, fingerprint_extensions=None):
        """
        Called outside, because we want to modify the config first
        """
        if fingerprint_extensions is None:
            fingerprint_extensions = []

        config_path = os.path.join(self.path, 'config.json')
        conf = Config(config_path)
        conf.set('site-url', 'http://example.com/')
        conf.set('fingerprint', fingerprint_extensions)
        conf.write()

        self.site = Site(self.path, config_path)

        self.site.build()

    def test_fingerprinting_off(self):
        """
        Test that fingerprinting can be disabled.
        """
        self.initialize()
        static = '/static/css/style.css'
        self.assertEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))

    def test_fingerprinting_on(self):
        """
        Test that fingerprinting provides existing URLs.
        """
        self.initialize(['css', 'js'])

        static = '/static/css/style.css'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))

        static = '/static/js/main.js'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))

    def test_fingerprinting_selective(self):
        """
        Test that fingerprinting can be restricted to certain filetypes.
        """
        self.initialize(['css'])

        static = '/static/css/style.css'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))

        static = '/static/js/main.js'
        self.assertEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))