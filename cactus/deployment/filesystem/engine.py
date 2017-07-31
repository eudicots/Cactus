#coding:utf-8
import logging
import os

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.filesystem.file import LocalFile
from cactus.utils.helpers import get_or_prompt
from cactus.utils.parallel import multiMap, PARALLEL_DISABLED

logger = logging.getLogger(__name__)


class FileSystemDeploymentEngine(BaseDeploymentEngine):
    FileClass = LocalFile

    config_website_directory = 'website-folder'

    def __init__(self, site):
        """
        :param site: An instance of cactus.site.Site
        """
        self.site = site

    def deploy(self):
        self.configure()

        if not os.path.exists(self.target_directory):
            logger.info("Website folder does not exist. Cancelling " \
                        "deployment.")
            return []

        # Upload all files concurrently in a thread pool
        mapper = multiMap
        if self.site._parallel <= PARALLEL_DISABLED:
            mapper = map

        totalFiles = mapper(lambda p: p.upload(), self.files())

        return totalFiles

    def configure(self):
        """
        This is when the DeploymentEngine should configure itself to prepare for deployment

        :rtype: None
        """
        target_directory_prompt = "Enter the website folder (must " \
                                  "be absolute, e.g.: /Users/dwight/MySite/)"
        self.target_directory = get_or_prompt(self.site.config, 
                                              self.config_website_directory,
                                              self.site.ui.prompt_normalized,
                                              target_directory_prompt)

        created = False
        if not os.path.isdir(self.target_directory):
            if self.site.ui.prompt_yes_no("Website folder does not " \
                                          "exist. Create it?"):
                os.makedirs(self.target_directory)
                created = True
            else:
                return

        self.site.config.write()

        website_endpoint = self.get_website_endpoint()
        if created:
            logger.info("Website folder %s was created with website " \
                        "endpoint %s", self.target_directory, website_endpoint)
        else:
            logger.info("Website folder: %s", self.target_directory)
        logger.info("Website: http://%s", website_endpoint)

    def get_website_endpoint(self):
        return os.path.basename(self.target_directory)
