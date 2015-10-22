#coding:utf-8
import sys
import os
import subprocess
from cactus.tests import BaseTestCase
from cactus.utils.filesystem import fileList


class CliTestCase(BaseTestCase):

    def setUp(self):
        super(CliTestCase, self).setUp()
        os.mkdir(self.path)
        self.site_a = os.path.join(self.path, 'site_a')
        self.site_b = os.path.join(self.path, 'site_b')

    def find_cactus(self):
        """
        Locate a Cactus executable and ensure that it'll run using the right interpreter.
        This is meant to work well in a Tox environment. That's how we run our tests, so that's all that really
        matters here.
        """
        bin_path = os.path.abspath(os.path.dirname(sys.executable))

        try:
            path = os.path.join(bin_path, "cactus")
            with open(path) as f:
                self.assertEqual("#!{0}".format(sys.executable), f.readline().strip())
        except IOError:
            pass
        else:
            return path

        try:
            path = os.path.join(bin_path, "cactus.exe")
            with open(path):
                pass
        except IOError:
            pass
        else:
            return path

        self.fail("Unable to find Cactus")

    def run_cli(self, args=[], stdin="", cwd=None):
        real_args = [self.find_cactus()] + args

        kwargs = {
            "args": real_args,
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "cwd": cwd,
        }

        p = subprocess.Popen(**kwargs)
        out, err = p.communicate(stdin.encode("utf-8"))
        return p.returncode, out, err

    def test_create_and_build(self):
        self.assertEqual(0, len(os.listdir(self.path)))

        # Test regular create
        ret, out, err = self.run_cli(["create", self.site_a, "--skeleton", os.path.join("cactus", "tests", "data", "skeleton")])
        self.assertEqual(0, ret)

        self.assertEqual(
            sorted(fileList(self.site_a, relative=True)),
            sorted(fileList("cactus/tests/data/skeleton", relative=True)),
        )

        # Test that we prompt to move stuff out of the way
        _, _, _ = self.run_cli(["create", "-v", self.site_a], "n\n")
        self.assertEqual(1, len(os.listdir(self.path)))

        _, _, _ = self.run_cli(["create", "-q", self.site_a], "y\n")
        self.assertEqual(2, len(os.listdir(self.path)))

        # Test that we can build the resulting site
        ret, _, _ = self.run_cli(["build"], cwd=self.site_a)
        self.assertEqual(0, ret)

        # Test that we can build a site in a custom folder
        ret, out, err = self.run_cli(["create", self.site_b, "--skeleton", os.path.join("cactus", "tests", "data", "skeleton")])
        self.assertEqual(0, ret)
        ret, _, _ = self.run_cli(["build", "--path", self.site_b], cwd=self.site_a)
        self.assertEqual(0, ret)

