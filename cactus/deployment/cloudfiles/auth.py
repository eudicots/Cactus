#coding:utf-8
from cactus.deployment.auth import BaseKeyringCredentialsManager


class CloudFilesCredentialsManager(BaseKeyringCredentialsManager):
    _username_config_entry = "cloudfiles-username"
    _password_display_name = "API Key"
    _keyring_service = "cactus/cloudfiles"
