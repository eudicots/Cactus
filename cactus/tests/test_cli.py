#coding:utf-8
import sys
import os
import os.path
import subprocess
from cactus.tests import BaseTestCase
from cactus.utils.filesystem import fileList


class CliTestCase(BaseTestCase):
    def find_cactus(self):
        """
        Locate a Cactus executable and ensure that it'll run using the right interpreter.
        This is meant to work well in a Tox environment. That's how we run our tests, so that's all that really
        matters here.
        """
        path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "cactus"))
        with open(path) as f:
            self.assertEqual("#!{0}".format(sys.executable), f.readline().strip())
        return path

    def run_cli(self, args, stdin="", cwd=None):
        real_args = [self.find_cactus()]
        real_args.extend(args)

        kwargs = {
            "args": real_args,
            "stdin":subprocess.PIPE,
            "stdout":subprocess.PIPE,
            "stderr":subprocess.PIPE,
        }

        if cwd is not None:
            kwargs["cwd"] = cwd


        p = subprocess.Popen(**kwargs)
        out, err = p.communicate(stdin.encode("utf-8"))
        return p.returncode, out, err

    def test_create_and_build(self):
        self.assertEqual(0, len(os.listdir(self.test_dir)))

        # Test regular create
        ret, out, err = self.run_cli(["create", self.path, "--skeleton", os.path.join("cactus", "tests", "data", "skeleton")])
        self.assertEqual(0, ret)

        self.assertEqual(
            sorted(fileList(self.path, relative=True)),
            sorted(fileList("cactus/tests/data/skeleton", relative=True)),
        )

        # Test that we prompt to move stuff out of the way
        _, _, _ = self.run_cli(["create", "-v", self.path], "n\n")
        self.assertEqual(1, len(os.listdir(self.test_dir)))

        _, _, _ = self.run_cli(["create", "-q", self.path], "y\n")
        self.assertEqual(2, len(os.listdir(self.test_dir)))

        # Test that we can build the resulting site
        ret, _, _ = self.run_cli(["build"], cwd=self.path)
        self.assertEqual(0, ret)



