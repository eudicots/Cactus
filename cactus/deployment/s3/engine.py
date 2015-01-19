#coding:utf-8
from __future__ import print_function
import logging

from boto import s3
from boto.exception import S3ResponseError, S3CreateError
from boto.route53.exception import DNSServerError

from cactus.deployment.engine import BaseDeploymentEngine
from cactus.deployment.s3.auth import AWSCredentialsManager
from cactus.deployment.s3.file import S3File
from cactus.deployment.s3.domain import AWSBucket, AWSDomain
from cactus.exceptions import InvalidCredentials
from cactus.utils import ipc


logger = logging.getLogger(__name__)


class S3DeploymentEngine(BaseDeploymentEngine):
    FileClass = S3File
    CredentialsManagerClass = AWSCredentialsManager

    config_bucket_name = "aws-bucket-name"
    config_bucket_website = "aws-bucket-website"
    config_bucket_region = "aws-bucket-region"

    _s3_default_region = "us-east-1"
    _s3_port = 443
    _s3_is_secure = True
    _s3_https_connection_factory = None


    def _get_buckets(self):
        """
        :returns: The list of buckets found for this account
        """
        try:
            return self.get_connection().get_all_buckets()
        except S3ResponseError as e:
            if e.error_code == u'InvalidAccessKeyId':
                logger.info("Received an Error from AWS:\n %s", e.body)
                raise InvalidCredentials()
            raise

    def _get_bucket_region(self):
        return self.site.config.get(self.config_bucket_region, self._s3_default_region)

    def _create_connection(self):
        """
        Create a new S3 Connection
        """
        aws_access_key, aws_secret_key = self.credentials_manager.get_credentials()

        return s3.connect_to_region(self._get_bucket_region(),
                aws_access_key_id=aws_access_key.strip(),
                aws_secret_access_key=aws_secret_key.strip(),
                is_secure=self._s3_is_secure, port=self._s3_port,
                https_connection_factory=self._s3_https_connection_factory,
                calling_format='boto.s3.connection.OrdinaryCallingFormat'
        )

    def get_bucket(self):
        """
        :returns: The Bucket if found, None otherwise.
        :raises: InvalidCredentials if we can't connect to AWS
        """
        buckets = self._get_buckets()
        buckets = dict((bucket.name, bucket) for bucket in buckets)
        return buckets.get(self.bucket_name)

    def create_bucket(self):
        """
        :returns: The newly created bucket
        """
        try:

            # When creating a bucket, the region cannot be "us-east-1" but needs
            # to be an empty string, so we do that for now.
            # https://github.com/boto/boto3/issues/125#issuecomment-109408790
            if self._get_bucket_region() == "us-east-1":
                region = ""
            else:
                region = self._get_bucket_region()

            bucket = self.get_connection().create_bucket(self.bucket_name,
                policy='public-read', location=region
            )
        except S3CreateError:
            logger.info(
                    'Bucket with name %s already is used by someone else, '
                    'please try again with another name', self.bucket_name)
            return  #TODO: These should be exceptions

        # Configure S3 to use the index.html and error.html files for indexes and 404/500s.
        bucket.configure_website(self._index_page, self._error_page)

        return bucket

    def get_website_endpoint(self):
        return self.bucket.get_website_endpoint()

    def domain_setup(self):
        bucket_name = self.site.config.get(self.config_bucket_name)
        bucket_name = self.site.config.get(self.config_bucket_name)

        if not bucket_name:
            logger.warning("No bucket name")
            return

        aws_access_key, aws_secret_key = self.credentials_manager.get_credentials()
        domain = AWSDomain(aws_access_key, aws_secret_key, bucket_name)

        try:
            domain.setup()
        except DNSServerError as e:
            logger.debug(e)
            ipc.signal("domain.setup.error", {"errorKey": "AccountDisabled"})
            logger.error("Account cannot use route 53")
            logger.error(e)

    def domain_list(self):
        bucket_name = self.site.config.get(self.config_bucket_name)

        if not bucket_name:
            logger.warning("No bucket name")
            return

        aws_access_key, aws_secret_key = self.credentials_manager.get_credentials()
        domain = AWSDomain(aws_access_key, aws_secret_key, bucket_name)

        try:
            domain_list = domain.nameServers()
        except DNSServerError as e:
            print(e)
            ipc.signal("domain.list.error", {"errorKey": "AccountDisabled"})
            logger.error("Account cannot use route 53")
            logger.error(e)
            return

        if domain_list:
            ipc.signal("domain.list.result", {"nameservers": domain_list})
            for domain in domain_list:
                logger.info(domain)
        else:
            logger.error("No name servers configured")


    def domain_remove(self):
        pass
