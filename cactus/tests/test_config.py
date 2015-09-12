#coding:utf-8
import os
import shutil
import tempfile
import unittest2 as unittest

from cactus.config.file import ConfigFile
from cactus.config.router import ConfigRouter

class TestConfigRouter(unittest.TestCase):
    """
    Test that the config router manages multiple files correctly.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, "test")
        os.mkdir(self.path)

        self.path1 = os.path.join(self.path, "conf1.json")
        self.path2 = os.path.join(self.path, "conf2.json")
        self.conf1 = ConfigFile(self.path1)
        self.conf2 = ConfigFile(self.path2)

        self.conf1.set("a", 1)
        self.conf1.write()
        self.conf2.set("b", 2)
        self.conf2.write()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read(self):
        """
        Check that the config router reads correctly from the filesystem
        """
        router = ConfigRouter([self.path1, self.path2])

        self.assertEqual(router.get("a"), 1)
        self.assertEqual(router.get("b"), 2)
        self.assertEqual(router.get("c"), None)

    def test_read_write(self):
        """
        Check that our config is readable after writing it
        """
        router = ConfigRouter([self.path1, self.path2])

        router.set("a", 3)
        router.set("b", 4)

        self.assertEqual(3, router.get("a"))
        self.assertEqual(4, router.get("b"))

    def test_write(self):
        """
        Check that the config router writes correctly to the filesystem
        """
        router = ConfigRouter([self.path1, self.path2])
        router.set("a", 3)
        router.set("b", 4)
        router.write()

        self.conf1.load()
        self.conf2.load()

        self.assertEqual(self.conf1.get("a"), 3)
        self.assertEqual(self.conf1.get("b"), None)
        self.assertEqual(self.conf2.get("b"), 4)
        self.assertEqual(self.conf2.get("a"), None)

    def test_collision(self):
        """
        Check that we get the right key when there is a collision
        """
        self.conf1.set("b", 3)
        self.conf2.set("a", 4)
        self.conf1.write()
        self.conf2.write()

        router = ConfigRouter([self.path1, self.path2])

        self.assertEqual(router.get("a"), 1)
        self.assertEqual(router.get("b"), 3)

    def test_duplicate(self):
        """
        Check that the config router handles duplicate files properly.
        """
        router = ConfigRouter([self.path1, self.path1])
        router.set("a", 3)
        router.write()

        self.conf1.load()
        self.assertEqual(self.conf1.get("a"), 3)

    def test_nested(self):
        """
        Test that we support nested config for context
        """
        self.conf1.set("context", {"k1":"v1"})
        self.conf2.set("context", {"k2":"v2"})
        self.conf1.write()
        self.conf2.write()

        router = ConfigRouter([self.path1, self.path2])
        context = router.get("context", default={}, nested=True)

        self.assertEqual(context.get("k1"), "v1")
        self.assertEqual(context.get("k2"), "v2")

    def test_dirty(self):
        """
        Test that we don't re-write files that we haven't changed
        """

        self.conf1.set("a", "b")
        self.conf1.write()

        with open(self.path1, "w") as f:
            f.write("canary")

        self.conf1.write()

        with open(self.path1) as f:
            self.assertEqual("canary", f.read())

    def test_missing_file(self):
        """
        Test that we don't throw on a missing file, and that the configuration
        remains in a consistent state.
        """
        wrong_path = os.path.join(self.path, "does_not_exist.json")

        self.conf1.set("context", {"k1":"v1"})
        self.conf1.write()

        router = ConfigRouter([wrong_path, self.path1])

        self.assertEqual(router.get("context").get("k1"), "v1")

    def test_broken_file(self):
        """
        Test that we don't throw on a broken file, and that the configuration
        remains in a consistent state.
        """

        with open(self.path1, "w") as f:
            f.write("{broken}")

        self.conf2.set("context", {"k1":"v1"})
        self.conf2.write()

        router = ConfigRouter([self.path1, self.path2])

        self.assertEqual(router.get("context").get("k1"), "v1")

