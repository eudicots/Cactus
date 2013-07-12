#coding:utf-8
from cactus.file import File
from cactus.utils.filesystem import fileList


class DeploymentEngine(object):
    def __init__(self, site):
        """
        :param site: An instance of cactus.site.Site
        """
        self.site = site

    def files(self):
        """
        List of build files.
        """
        return [File(self.site, file_path) for file_path in fileList(self.site.build_path, relative=True)]
