#coding:utf-8
import unittest

from cactus.mime import guess


class MimeTestCase(unittest.TestCase):
    def test_mime_eot(self):
        font_path = "test/font.eot"
        self.assertFalse(guess(font_path) is None)

    def test_mime_dummy(self):
        # Make sure we never return a None mime type!
        path = "test/format.thisisnomime"
        self.assertFalse(guess(path) is None)
