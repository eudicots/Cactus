#coding:utf-8
import logging

import boto
from boto.exception import S3ResponseError

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.s3.file import S3File
from cactus.exceptions import InvalidCredentials


class S3DeploymentEngine(BaseDeploymentEngine):
    _s3_api_endpoint = 's3.amazonaws.com'
    _s3_port = 443
    _s3_is_secure = True
    _s3_https_connection_factory = None

    FileClass = S3File

    def get_connection(self):
        """
        Create a new S3 Connection
        """
        credentials = self.site.credentials_manager.get_credentials()
        aws_access_key = credentials["access_key"]
        aws_secret_key = credentials["secret_key"]

        return boto.connect_s3(aws_access_key.strip(), aws_secret_key.strip(),
                               host=self._s3_api_endpoint, is_secure=self._s3_is_secure, port=self._s3_port,
                               https_connection_factory=self._s3_https_connection_factory)

    def create_bucket(self, connection, bucket_name):
        """
        :param connection: An S3Connection to use
        :param bucket_name: The name of the bucket to create
        :returns: The newly created bucket
        """
        try:
            bucket = connection.create_bucket(bucket_name, policy='public-read')
        except boto.exception.S3CreateError:
            logging.info(
                'Bucket with name %s already is used by someone else, '
                'please try again with another name', bucket_name)
            return

        # Configure S3 to use the index.html and error.html files for indexes and 404/500s.
        bucket.configure_website('index.html', 'error.html')

        return bucket

    def get_buckets(self, connection):
        """
        :param connection: An S3Connection to use
        :returns: The list of buckets found for this account
        """
        try:
            return connection.get_all_buckets()
        except S3ResponseError as e:
            if e.error_code == u'InvalidAccessKeyId':
                logging.info("Received an Error from AWS:\n %s", e.body)
                raise InvalidCredentials()
            raise

    def get_bucket(self, connection, bucket_name):
        """
        :param connection: An S3Connection to use
        :param bucket_name: The bucket to look for
        :returns: The Bucket if found, None otherwise.
        :raises: InvalidCredentials if we can't connect to AWS
        """
        buckets = self.get_buckets(connection)
        buckets = dict((bucket.name, bucket) for bucket in buckets)
        return buckets.get(bucket_name)

    def configure(self):
        """
        Upload the site to the server.
        """
        bucket_name = self.site.config.get('aws-bucket-name')
        if bucket_name is None:
            bucket_name = self.site.ui.prompt_normalized("S3 bucket name (www.yoursite.com)")

        try:
            connection = self.get_connection()
            bucket = self.get_bucket(connection, bucket_name)
        except InvalidCredentials:
            logging.fatal("Invalid AWS credentials")
            return

        created = False

        if bucket is None:
            if self.site.ui.prompt_yes_no("Bucket does not exist. Create it?"):
                bucket = self.create_bucket(connection, bucket_name)
                created = True
            else:
                return

        self.bucket = bucket

        website_endpoint = bucket.get_website_endpoint()

        if created:
            logging.info('Bucket %s was selected with website endpoint %s' % (
                bucket_name, website_endpoint))
            logging.info(
                'You can learn more about s3 (like pointing to your own domain)'
                ' here: https://github.com/koenbok/Cactus')

        # If the credentials were correct, save them for the future
        self.site.config.set('aws-bucket-name', bucket_name)
        self.site.config.set('aws-bucket-website', website_endpoint)
        self.site.config.write()

        self.site.credentials_manager.save_credentials()

        logging.info("Bucket Name: %s", bucket_name)
        logging.info("Bucket Web Endpoint: %s", website_endpoint)
