#coding:utf-8


class DummyAWSCredentialsManager(object):
    def __init__(self, site):
        self.site = site

    def get_credentials(self):
        return {
            "access_key": "123",
            "secret_key": "abc"
        }

    def save_credentials(self):
        pass
