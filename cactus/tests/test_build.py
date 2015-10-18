#coding:utf-8
import os
import tempfile
import unittest2 as unittest

from cactus.tests import SiteTestCase
from cactus.tests.compat import has_symlink


class TestBuild(SiteTestCase):

    @unittest.skipUnless(has_symlink, "No symlink support")
    def test_existing_symlink(self):

        with open(os.path.join(self.site.static_path, 'file.js'), "w") as f:
            f.write("hello")

        os.symlink(
            os.path.join(self.site.static_path, 'file.js'),
            os.path.join(self.site.static_path, 'file-link.js'))

        self.site.build()

        self.assertFileExists(os.path.join(self.site.build_path, 'static', 'file.js'))
        self.assertFileExists(os.path.join(self.site.build_path, 'static', 'file-link.js'))

        with open(os.path.join(self.site.build_path, 'static', 'file-link.js')) as f:
            self.assertEqual(f.read(), "hello")

        self.assertEqual(
            os.path.islink(os.path.join(self.site.build_path, 'static', 'file-link.js')), False)

    @unittest.skipUnless(has_symlink, "No symlink support")
    def test_nonexisting_symlink(self):

        os.symlink(
            os.path.join(self.site.static_path, 'file.js'),
            os.path.join(self.site.static_path, 'file-link.js'))

        self.site.build()

        self.assertFileDoesNotExist(os.path.join(self.site.build_path, 'static', 'file.js'))
        self.assertFileDoesNotExist(os.path.join(self.site.build_path, 'static', 'file-link.js'))

    def test_pages_binary_file(self):

        with open(os.path.join(self.site.page_path, 'file.zip'), "wb") as f:
            f.write(os.urandom(1024))

        self.site.build()

    def test_listener_ignores(self):

        # Some complete;y random files
        self.assertEqual(True, self.site._rebuild_should_ignore("/Users/test/a.html"))
        self.assertEqual(True, self.site._rebuild_should_ignore("a.html"))
        self.assertEqual(True, self.site._rebuild_should_ignore("/a.html"))

        # Some plausible files
        self.assertEqual(True, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "config.json")))
        self.assertEqual(True, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "readme.txt")))
        self.assertEqual(True, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, ".git", "config")))
        self.assertEqual(True, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, ".build", "index.html")))
        self.assertEqual(True, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, ".build", "static", "main.js")))

        # Files we do want
        self.assertEqual(False, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "pages", "index.html")))
        self.assertEqual(False, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "pages", "staging", "index.html")))
        self.assertEqual(False, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "templates", "base.html")))
        self.assertEqual(False, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "static", "main.js")))
        self.assertEqual(False, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "plugins", "test.py")))

        # Dotfile stuff
        self.assertEqual(True, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "pages", ".DS_Store")))
        self.assertEqual(True, self.site._rebuild_should_ignore(
            os.path.join(self.site.path, "pages", ".hidden", "a.html")))

    @unittest.skipUnless(has_symlink, "No symlink support")
    def test_symlink_ignore(self):

        file_path = os.path.join(tempfile.mkdtemp(), 'file.js')
        link_path = os.path.join(self.site.static_path, 'file-link.js')

        with open(file_path, "w") as f:
            f.write("hello")

        os.symlink(file_path, link_path)

        # Test for ignore function to work with symlinks
        self.assertEqual(self.site._rebuild_should_ignore(link_path), False)
