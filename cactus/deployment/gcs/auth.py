#coding:utf-8
import webbrowser

from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from oauth2client.keyring_storage import Storage

from cactus.deployment.gcs import CACTUS_CLIENT_ID, CACTUS_CLIENT_SECRET, CACTUS_REQUIRED_SCOPE, LOCAL_REDIRECT_URI
from cactus.exceptions import InvalidCredentials


class GCSCredentialsManager(object):
    def __init__(self, engine):
        self.engine = engine  #TODO: Only pass those things that are needed?
        self.credentials = None

    def get_storage(self):
        return Storage("cactus/gcs", self.engine.bucket_name)  #TODO: Not a great key, but do we want to ask for email?

    def get_credentials(self):

        if self.credentials is not None:
            return self.credentials

        self.credentials = self.get_storage().get()

        if self.credentials is None:
            flow = OAuth2WebServerFlow(
                client_id=CACTUS_CLIENT_ID,
                client_secret=CACTUS_CLIENT_SECRET,
                scope=CACTUS_REQUIRED_SCOPE,
                redirect_uri=LOCAL_REDIRECT_URI
            )

            auth_uri = flow.step1_get_authorize_url()
            webbrowser.open(auth_uri)  #TODO: Actually print the URL...
            code = self.engine.site.ui.prompt('Please enter the authorization code')

            try:
                self.credentials = flow.step2_exchange(code)  #TODO: Catch invalid grant
            except FlowExchangeError:
                raise InvalidCredentials("The authorization did not match.")

        return self.credentials

    def save_credentials(self):
        assert self.credentials is not None, "You did not set credentials before saving them"  #TODO: That's still bad
        self.get_storage().put(self.credentials)
