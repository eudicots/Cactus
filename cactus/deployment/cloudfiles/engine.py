#coding:utf-8

import pyrax

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.cloudfiles.auth import CloudFilesCredentialsManager
from cactus.deployment.cloudfiles.file import CloudFilesFile


class CloudFilesDeploymentEngine(BaseDeploymentEngine):
    CredentialsManagerClass = CloudFilesCredentialsManager
    FileClass = CloudFilesFile

    config_bucket_name = "cloudfiles-bucket-name"
    config_bucket_website = "cloudfiles-bucket-website"

    def _create_connection(self):
        username, api_key = self.credentials_manager.get_credentials()
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_credentials(username, api_key)
        return pyrax.connect_to_cloudfiles()

    def get_bucket(self):
        try:
            return self.get_connection().get_container(self.bucket_name)
        except pyrax.exceptions.NoSuchContainer:
            return None

    def create_bucket(self):
        #TODO: Handle errors
        conn = self.get_connection()
        container = conn.create_container(self.bucket_name)
        container.set_web_index_page(self._index_page)
        container.set_web_error_page(self._error_page)
        container.make_public()
        return container

    def get_website_endpoint(self):
        return self.bucket.cdn_uri
