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
        self.build_path = self.site.paths['build']

        self.site.build()

    def test_fingerprinting_off(self):
        self.initialize()
        static = '/static/css/style.css'
        self.assertEqual(self.site.get_url_for_static(static), static)

    def test_fingerprinting_on(self):
        self.initialize(['css', 'js'])
        static = '/static/css/style.css'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        static = '/static/js/main.js'
        self.assertNotEqual(self.site.get_url_for_static(static), static)

    def test_fingerprinting_selective(self):
        self.initialize(['css'])
        static = '/static/css/style.css'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        static = '/static/js/main.js'
        self.assertEqual(self.site.get_url_for_static(static), static)