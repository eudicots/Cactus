#coding:utf-8
import getpass
import keyring

class BaseKeyringCredentialsManager(object):
    _username_config_entry = "username"
    _keyring_service = "cactus"

    _username_display_name = "Username"
    _password_display_name = "Password"

    def __init__(self, engine):
        self.engine = engine  #TODO: Don't we want only UI and config?
        self.username = None
        self.password = None

    def get_credentials(self):
        self.username = self.engine.site.config.get(self._username_config_entry)
        if self.username is None:
            self.username = self.engine.site.ui.prompt("Enter your {0}".format(self._username_display_name))

        self.password = keyring.get_password(self._keyring_service, self.username)
        if self.password is None:
            self.password = self.engine.site.ui.prompt("Enter your {0} (will not be echoed)".format(self._password_display_name),
                prompt_fn=getpass.getpass)

        return self.username, self.password

    def save_credentials(self):
        assert self.username is not None, "You did not set {0}".format(self._username_display_name)
        assert self.password is not None, "You did not set {0}".format(self._password_display_name)

        self.engine.site.config.set(self._username_config_entry, self.username)
        self.engine.site.config.write()

        keyring.set_password(self._keyring_service, self.username, self.password)
