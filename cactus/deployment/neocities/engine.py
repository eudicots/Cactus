#coding:utf-8
import logging
import requests

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.neocities.auth import NeocitiesCredentialsManager
from cactus.deployment.neocities.rest import NeocitiesRest

logger = logging.getLogger(__name__)

class NeocitiesDeploymentEngine(BaseDeploymentEngine):
    RestClass = NeocitiesRest
    CredentialsManagerClass = NeocitiesCredentialsManager

    def __init__(self, *args, **kwargs):
        super(NeocitiesDeploymentEngine, self).__init__(*args, **kwargs)
        self.rest_api = self.RestClass()

    def deploy(self):
        self.configure()
        result = self.upload()
        if result:
            return map(lambda file: {'changed': True, 'size': len(file.payload())}, self.files())
            self.save_credentials()
        else:
            return []

    def get_credentials(self):
        return self.credentials_manager.get_credentials()

    def save_credentials(self):
        self.site.config.write()
        self.credentials_manager.save_credentials()

    def configure(self):
        user, password = self.get_credentials()

        self.rest_api.connect(user, password)

        logger.info("Set upload path to site: " + user)

    def upload(self):
        return self.rest_api.upload(self.file_map())   

    def file_map(self):
        return map(lambda file: (file.url, file.payload()), self.files())
