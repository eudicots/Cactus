#coding:utf-8
import os
import shutil
from cactus.plugin.manager import PluginManager

from cactus.site import Site

from cactus.tests import BaseTestCase
from cactus.tests.integration.http import DebugHTTPSConnectionFactory
from cactus.utils.parallel import PARALLEL_DISABLED


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
    def setUp(self):
        super(IntegrationTestCase, self).setUp()

        self.site = Site(self.path,
            PluginManagerClass=DummyPluginManager, DeploymentEngineClass=self.get_deployment_engine_class())
        self.site._parallel = PARALLEL_DISABLED

        self.site.config.set('site-url', 'http://example.com/')

        # Clean up the site paths
        for path in (self.site.page_path, self.site.static_path):
            shutil.rmtree(path)
            os.mkdir(path)

    def get_deployment_engine_class(self):
        """
        Should return a deployment engine in tests.
        """
        pass
