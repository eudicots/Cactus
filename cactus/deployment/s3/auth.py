#coding:utf-8
import getpass
from cactus.utils import password

#TODO: Use the keyring module

class AWSCredentialsManager(object):
    access_key = None
    secret_key = None

    def __init__(self, engine, password_manager=None):
        """
        :param engine: A deployment engine instance (used to access the site and its config)
        :param password_manager: A password manager to use. Should implement
            setpassword(service, account): persist a password
            getpassword(service, account, password): retrieve a persisted password
        """
        self.engine = engine

        if password_manager is None:
            password_manager = password
        self.password_manager = password_manager

    def get_credentials(self):
        """
        MAC OS, AWS... for the moment!
        """
        self.access_key = self.engine.site.config.get('aws-access-key')
        if self.access_key is None:
            self.access_key = raw_input('Amazon access key (http://bit.ly/Agl7A9): ').strip()

        self.secret_key = self.password_manager.get_password('aws', self.access_key)
        if self.secret_key is None:
            self.secret_key = getpass._raw_input('Amazon secret access key (will be saved in keychain): ').strip()

        return {"access_key": self.access_key, "secret_key": self.secret_key}

    def save_credentials(self):
        """
        If the credentials were correct - save them.
        """
        assert self.access_key is not None, "You did not load the access key first!"
        assert self.secret_key is not None, "You did not load the secret key first!"

        self.engine.site.config.set('aws-access-key', self.access_key)
        self.engine.site.config.write()

        self.password_manager.set_password('aws', self.access_key, self.secret_key)