#coding:utf-8
import os
import shutil
from cactus.plugin.manager import PluginManager

from cactus.site import Site
from cactus.deployment.s3 import S3DeploymentEngine

from cactus.tests import BaseTestCase
from cactus.tests.integration.credentials import DummyAWSCredentialsManager
from cactus.tests.integration.http import DebugHTTPSConnectionFactory


class DummyPluginManager(PluginManager):
    """
    Doesn't do anything
    """
    def call(self, method, *args, **kwargs):
        """
        Trap the call
        """
        pass


class IntegrationTestCase(BaseTestCase):
    connection_class = None

    def setUp(self):
        super(IntegrationTestCase, self).setUp()

        # Create a connection factory
        self.connection_factory = DebugHTTPSConnectionFactory(self.connection_class)


        # Instantiate our site
        class TestS3DeploymentEngine(S3DeploymentEngine):
            _s3_https_connection_factory = (self.connection_factory, ())

        self.site = Site(self.path,
            PluginManagerClass=DummyPluginManager, CredentialsManagerClass=DummyAWSCredentialsManager,
            DeploymentEngineClass=TestS3DeploymentEngine)

        self.site.config.set('site-url', 'http://example.com/')

        # Clean up the site paths
        for path in (self.site.page_path, self.site.static_path):
            shutil.rmtree(path)
            os.mkdir(path)
