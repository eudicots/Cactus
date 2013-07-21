#coding:utf-8
from cactus.deployment.auth import BaseKeyringCredentialsManager


class AWSCredentialsManager(BaseKeyringCredentialsManager):
    _username_config_entry = "aws-access-key"
    _username_display_name = "Amazon Access Key ID"
    _password_display_name = "Amazon Secret Access Key"
    _keyring_service = "aws"  #Would break backwards compatibility
