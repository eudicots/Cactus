#coding:utf-8
import logging
from cactus.deployment.file import BaseFile
from cactus.utils.filesystem import fileList
from cactus.utils.helpers import get_or_prompt
from cactus.utils.parallel import multiMap, PARALLEL_DISABLED


class BaseDeploymentEngine(object):
    FileClass = BaseFile
    CredentialsManagerClass = None  #TODO: Define interface?

    config_bucket_name = None
    config_bucket_website = None

    _index_page = "index.html"
    _error_page = "error.html"

    _connection = None

    def __init__(self, site, CredentialsManagerClass=None):
        """
        :param site: An instance of cactus.site.Site
        """
        self.site = site

        if CredentialsManagerClass is None:
            CredentialsManagerClass = self.CredentialsManagerClass
        self.credentials_manager = CredentialsManagerClass(self)

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

    def get_connection(self):
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    def _create_connection(self):
        """
        Should return a Connection object
        """
        raise NotImplementedError()

    def get_bucket(self):
        """
        Should return a Bucket object, None if the bucket does not exist.
        """
        raise NotImplementedError()

    def create_bucket(self):
        """
        Should create and return a Bucket object.
        """
        raise NotImplementedError()

    def get_website_endpoint(self):
        """
        Should return the Website endpoint for the bucket.
        """
        #TODO: Normalize -- rackspace gives an URL, but Amazon gives a domain name
        raise NotImplementedError()

    def configure(self):
        """
        This is when the DeploymentEngine should configure itself to prepare for deployment

        :rtype: None
        """
        self.bucket_name = get_or_prompt(self.site.config, self.config_bucket_name, self.site.ui.prompt_normalized,
                                         "Enter the bucket name (e.g.: www.example.com)")

        self.bucket = self.get_bucket()  #TODO: Catch auth errors

        #TODO: Make this all integrated and consistent!
        created = False
        if self.bucket is None:
            if self.site.ui.prompt_yes_no("Bucket does not exist. Create it?"):
                self.bucket = self.create_bucket()
                created = True
            else:
                return

        website_endpoint = self.get_website_endpoint()
        self.site.config.set(self.config_bucket_website, website_endpoint)

        self.site.config.write()
        self.credentials_manager.save_credentials()

        if created:
            logging.info('Bucket %s was created with website endpoint %s',  self.bucket_name, website_endpoint)

        logging.info("Bucket Name: %s", self.bucket_name)
        logging.info("Bucket Web Endpoint: %s", website_endpoint)
