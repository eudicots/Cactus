#coding:utf-8
import webbrowser

from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from oauth2client.keyring_storage import Storage

from cactus.deployment.gcs import CACTUS_CLIENT_ID, CACTUS_CLIENT_SECRET, CACTUS_REQUIRED_SCOPE, LOCAL_REDIRECT_URI
from cactus.exceptions import InvalidCredentials


class GCSCredentialsManager(object):
    def __init__(self, engine):
        self.engine = engine

    def get_credentials(self, bucket_name):
        storage = Storage("cactus/gcs", bucket_name)

        credentials = storage.get()

        if credentials is None:
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
                credentials = flow.step2_exchange(code)  #TODO: Catch invalid grant
            except FlowExchangeError:
                raise InvalidCredentials("The authorization did not match.")

            storage.put(credentials)

        return credentials
