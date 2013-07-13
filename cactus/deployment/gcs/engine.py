#coding:utf-8
import logging
import httplib2

import apiclient.discovery
import apiclient.errors

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.gcs.auth import GCSCredentialsManager
from cactus.deployment.gcs.file import GCSFile
from cactus.exceptions import InvalidCredentials


class GCSDeploymentEngine(BaseDeploymentEngine):
    _HTTPClass = httplib2.Http
    FileClass = GCSFile
    CredentialsManagerClass = GCSCredentialsManager

    def create_bucket(self, service, project_id, bucket_name):
        public_acl = {
            "entity": "allUsers",
            "role": "READER",
        }

        body = {
            "name": bucket_name,
            "website": {
                "mainPageSuffix": "index.html", #TODO: Constant
                "notFoundPage": "error.html",  #TODO: Constant
            },
            "defaultObjectAcl": [public_acl], #TODO: Not required actually
        }

        service.buckets().insert(project=project_id, body=body).execute()
        return self.get_bucket(service, bucket_name)

    def get_bucket(self, service, bucket_name):
        req = service.buckets().get(bucket=bucket_name)
        try:
            return req.execute()
        except apiclient.errors.HttpError as e:
            if e.resp['status'] == '404':
                return None
            raise

    def configure(self):
        self.http_client = self._HTTPClass()

        bucket_name = self.site.config.get('gcs-bucket-name')
        if bucket_name is None:
            bucket_name = self.site.ui.prompt_normalized('GCS bucket name (www.yoursite.com)')
            self.site.config.set('gcs-bucket-name', bucket_name)
            self.site.config.write()

        try:
            self.credentials_manager.authorize(bucket_name, self.http_client)
        except InvalidCredentials:
            logging.fatal("Invalid GCE credentials")
            return

        service = apiclient.discovery.build('storage', 'v1beta2', http=self.http_client)

        bucket = self.get_bucket(service, bucket_name)

        #TODO: Merge some workflow logic with the AWS client
        created = False
        if bucket is None:
            if self.site.ui.prompt_yes_no("Bucket does not exist. Create it?"):
                project_id = self.site.ui.prompt_normalized('API project identifier?')
                self.create_bucket(service, project_id, bucket_name)
                created = True
            else:
                return

        if created:
            logging.info('Bucket %s was selected with website endpoint',  bucket_name)
            logging.info(
                'You can learn more about s3 (like pointing to your own domain)'
                ' here: https://github.com/koenbok/Cactus')

        self.service = service
        self.bucket_name = bucket_name