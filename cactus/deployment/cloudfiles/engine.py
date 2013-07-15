#coding:utf-8
import logging

import pyrax

from cactus.utils.helpers import get_or_prompt
from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.cloudfiles.auth import CloudFilesCredentialsManager
from cactus.deployment.cloudfiles.file import CloudFilesFile


class CloudFilesDeploymentEngine(BaseDeploymentEngine):
    CredentialsManagerClass = CloudFilesCredentialsManager
    FileClass = CloudFilesFile

    _connection = None

    def _create_connection(self):
        username, api_key = self.credentials_manager.get_credentials()
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_credentials(username, api_key)
        return pyrax.connect_to_cloudfiles()

    def get_connection(self):
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    def get_bucket(self, bucket_name):
        try:
            return self.get_connection().get_container(bucket_name)
        except pyrax.exceptions.NoSuchContainer as e:
            return None

    def create_bucket(self, bucket_name):
        #TODO: Handle errors
        conn = self.get_connection()
        container = conn.create_container(bucket_name)
        container.set_web_index_page("index.html")  #TODO: Constant
        container.set_web_error_page("error.html")  #TODO: Constant
        container.make_public()
        return container

    def get_website_endpoint(self, bucket):
        return bucket.cdn_uri


    def configure(self):
        bucket_name = get_or_prompt(self.site.config, "cloudfiles-bucket-name", self.site.ui.prompt_normalized,
                                    "Swift bucket name (www.example.com)")

        container = self.get_bucket(bucket_name)  #TODO: Catch auth errors

        #TODO: Make this all integrated and consistent!
        created = False
        if container is None:
            if self.site.ui.prompt_yes_no("Bucket does not exist. Create it?"):
                container = self.create_bucket(bucket_name)
                created = True
            else:
                return

        website_endpoint = self.get_website_endpoint(container)
        self.site.config.set("cloudfiles-bucket-website", website_endpoint)
        self.site.config.write()
        self.credentials_manager.save_credentials()

        if created:
            logging.info('Bucket %s was created with website endpoint %s',  bucket_name, website_endpoint)

        logging.info("Bucket Name: %s", bucket_name)
        logging.info("Bucket Web Endpoint: %s", website_endpoint)

        self.bucket = container