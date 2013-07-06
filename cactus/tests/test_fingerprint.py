#coding:utf-8
import os
from cactus.tests import SiteTestCase


class TestFingerPrintingMixin(object):
    fingerprint_extensions = None

    def get_config_for_test(self):
        return {"fingerprint": self.fingerprint_extensions}


class TestFingerprintingOff(TestFingerPrintingMixin, SiteTestCase):
    fingerprint_extensions = []

    def setUp(self):
        super(TestFingerprintingOff, self).setUp()
        self.site.build()

    def test_fingerprinting_off(self):
        """
        Test that fingerprinting can be disabled.
        """
        static = '/static/css/style.css'
        self.assertEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))


class TestFingerprintingOn(TestFingerPrintingMixin, SiteTestCase):
    fingerprint_extensions = ["css", "js"]

    def setUp(self):
        super(TestFingerprintingOn, self).setUp()
        self.site.build()

    def test_fingerprinting_on(self):
        """
        Test that fingerprinting provides existing URLs.
        """
        static = '/static/css/style.css'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))

        static = '/static/js/main.js'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))


class TestFingerprintingSelective(TestFingerPrintingMixin, SiteTestCase):
    fingerprint_extensions = ["css"]

    def setUp(self):
        super(TestFingerprintingSelective, self).setUp()
        self.site.build()

    def test_fingerprinting_selective(self):
        """
        Test that fingerprinting can be restricted to certain filetypes.
        """
        static = '/static/css/style.css'
        self.assertNotEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))

        static = '/static/js/main.js'
        self.assertEqual(self.site.get_url_for_static(static), static)
        self.assertFileExists(os.path.join(self.site.build_path, self.site.get_url_for_static(static)[1:]))