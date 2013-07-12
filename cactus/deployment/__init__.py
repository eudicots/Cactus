#coding:utf-8
from cactus.deployment.file import BaseFile
from cactus.utils.filesystem import fileList


class BaseDeploymentEngine(object):
    FileClass = BaseFile

    def __init__(self, site):
        """
        :param site: An instance of cactus.site.Site
        """
        self.site = site

    def files(self):
        """
        List of build files.
        """
        return [self.FileClass(self, file_path) for file_path in fileList(self.site.build_path, relative=True)]
