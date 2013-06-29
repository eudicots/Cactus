#coding:utf-8

from cactus.tests import BaseTest
from cactus.utils.filesystem import fileList


class TestBootstrap(BaseTest):
    def testBootstrap(self):
        self.assertEqual(
            sorted(fileList(self.path, relative=True)),
            sorted(fileList("cactus/skeleton", relative=True)),
        )