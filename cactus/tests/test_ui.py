#coding:utf-8
import unittest2 as unittest

from cactus import ui


class UITestCase(unittest.TestCase):
    def test_coerce_yes_no(self):
        self.assertEqual(True, ui._yes_no_coerce_fn("y"))
        self.assertEqual(True, ui._yes_no_coerce_fn("Y"))

        self.assertEqual(False, ui._yes_no_coerce_fn("n"))
        self.assertEqual(False, ui._yes_no_coerce_fn("N"))

        self.assertRaises(ui.InvalidInput, ui._yes_no_coerce_fn, "True")
        self.assertRaises(ui.InvalidInput, ui._yes_no_coerce_fn, "False")
        self.assertRaises(ui.InvalidInput, ui._yes_no_coerce_fn, "yes")
        self.assertRaises(ui.InvalidInput, ui._yes_no_coerce_fn, "no")

    def test_coerce_normalized(self):
        self.assertEqual("a", ui._normalized_coerce_fn("a "))
        self.assertEqual("a", ui._normalized_coerce_fn("A "))
        self.assertEqual("a", ui._normalized_coerce_fn(" A "))

    def test_coerce_url(self):
        self.assertEqual("http://www.example.com/", ui._url_coerce_fn("http://www.example.com/"))
        self.assertEqual("http://www.example.com/", ui._url_coerce_fn("http://www.EXAMPLE.com/"))
        self.assertEqual("http://www.example.com/", ui._url_coerce_fn("http://www.example.com"))

        self.assertRaises(ui.InvalidInput, ui._url_coerce_fn, "")
        self.assertRaises(ui.InvalidInput, ui._url_coerce_fn, "www.example.com")
        self.assertRaises(ui.InvalidInput, ui._url_coerce_fn, "www.example.com  ")
        self.assertRaises(ui.InvalidInput, ui._url_coerce_fn, "http://")
        self.assertRaises(ui.InvalidInput, ui._url_coerce_fn, "/")
        self.assertRaises(ui.InvalidInput, ui._url_coerce_fn, "http://www.example.com/somewhere/")
        self.assertRaises(ui.InvalidInput, ui._url_coerce_fn, "http://www.example.com/#hash")


# Disabled for now with the desktop app

# class InteractiveUITestCase(BaseTestCase):
#     def test_site_url_not_set(self):
#         class DummyUI(object):
#             def prompt_url(self, q):
#                 return "http://example.com"

#         site = Site(self.path, ui=DummyUI())
#         self.assertEqual(None, site.url)
#         site.build()
#         self.assertEqual("http://example.com", site.url)
