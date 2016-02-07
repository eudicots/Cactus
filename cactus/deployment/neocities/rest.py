import requests
import logging
import json
from pprint import pprint

from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

class NeocitiesRest:
    ApiEndpoint = "https://neocities.org/api"
    NeocitiesUploadAction = "/upload"
    #NeocitiesDeleteAction = "/delete"
    #NeocitiesInfoAction = "/info"

    def connect(self, sitename, password):
        self.sitename = sitename
        self.password = password

    def upload(self, files):
        if not self.sitename:
            raise "Invalid sitename specified, cannot upload files"

        endpoint = self.ApiEndpoint + self.NeocitiesUploadAction
        response = requests.post(endpoint, auth=HTTPBasicAuth(self.sitename, self.password), files=files)
        return self.handleResponse(response)

    def handleResponse(self, response):
        try:
            body = json.loads(response.content)
            response.raise_for_status()
        except:
            logger.error("Request returned a code: " + str(response.status_code))
            logger.info("Error: " + body['message'])
            return False
        else:
            logger.info("Response: " + body['message'])
            return True

