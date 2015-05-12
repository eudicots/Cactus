#coding:utf-8
import logging
import threading

import httplib2
import apiclient.discovery
import apiclient.errors

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.gcs.auth import GCSCredentialsManager
from cactus.deployment.gcs.file import GCSFile
from cactus.exceptions import InvalidCredentials


class GCSDeploymentEngine(BaseDeploymentEngine):
    FileClass = GCSFile
    CredentialsManagerClass = GCSCredentialsManager

    config_bucket_name = "gcs-bucket-name"
    config_bucket_website = "gcs-bucket-website"

    _HTTPClass = httplib2.Http


    def __init__(self, *args, **kwargs):
        super(GCSDeploymentEngine, self).__init__(*args, **kwargs)
        self._service_pool = {}  # We can't share services (they share SSL connections) across processes.

    def get_connection(self):
        """
        Worker threads may not share the same connection
        """
        thread = threading.current_thread()
        ident = thread.ident

        service = self._service_pool.get(ident)
        if service is None:
            credentials = self.credentials_manager.get_credentials()
            http_client = self._HTTPClass()
            credentials.authorize(http_client)
            service = apiclient.discovery.build('storage', 'v1', http=http_client)
            self._service_pool[ident] = service

        return service

    def get_bucket(self):
        req = self.get_connection().buckets().get(bucket=self.bucket_name)
        try:
            return req.execute()
        except apiclient.errors.HttpError as e:
            if e.resp['status'] == '404':
                return None
            raise

    def create_bucket(self):
        project_id = self.site.ui.prompt_normalized('API project identifier?')

        public_acl = {
            "entity": "allUsers",
            "role": "READER",
        }

        body = {
            "name": self.bucket_name,
            "website": {
                "mainPageSuffix": self._index_page,
                "notFoundPage": self._error_page,
            },
            "defaultObjectAcl": [public_acl], #TODO: Not required actually
        }

        self.get_connection().buckets().insert(project=project_id, body=body).execute()
        return self.get_bucket()

    def get_website_endpoint(self):
        return "Unavailable for GCS"
