#coding:utf-8

from cactus.tests import BaseTest
from cactus.utils.filesystem import fileList


class TestBootstrap(BaseTest):
    def testBootstrap(self):
        self.assertEqual(
            fileList(self.path, relative=True),
            fileList("cactus/skeleton", relative=True),
        )