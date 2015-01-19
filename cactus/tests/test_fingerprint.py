#coding:utf-8
from __future__ import unicode_literals

import os
import io
import hashlib

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


class TestFingerprintingValues(TestFingerPrintingMixin, SiteTestCase):
    fingerprint_extensions = ["dat"]

    def test_fingerprinting_hashes(self):
        payload = b"\x01" * 131072  # (2**17 bytes = 2 * 65536)
        expected_checksum = hashlib.md5(payload).hexdigest()

        with io.FileIO(os.path.join(self.path, "static", "data.dat"), "w") as f:
            f.write(payload)

        self.site.build()
        self.assertTrue(expected_checksum in self.site.get_url_for_static("/static/data.dat"))
