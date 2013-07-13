#coding:utf-8
from cactus.deployment.file import BaseFile
from cactus.utils.filesystem import fileList
from cactus.utils.parallel import multiMap, PARALLEL_DISABLED


class BaseDeploymentEngine(object):
    FileClass = BaseFile

    def __init__(self, site, CredentialsManagerClass=None):
        """
        :param site: An instance of cactus.site.Site
        """
        self.site = site

    def deploy(self):
        self.configure()

        # Upload all files concurrently in a thread pool
        mapper = multiMap
        if self.site._parallel <= PARALLEL_DISABLED:
            mapper = map

        totalFiles = mapper(lambda p: p.upload(), self.files())

        return totalFiles

    def files(self):
        """
        List of build files.
        """
        return [self.FileClass(self, file_path) for file_path in fileList(self.site.build_path, relative=True)]

    def configure(self):
        """
        This is when the DeploymentEngine should configure itself to prepare for deployment

        :rtype: None
        """
        raise NotImplementedError()