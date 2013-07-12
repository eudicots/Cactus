#coding:utf-8
import os
import shutil
from cactus.plugin.manager import PluginManager

from cactus.tests import SiteTestCase
from cactus.tests.integration.credentials import DummyAWSCredentialsManager
from cactus.tests.integration.http import DebugHTTPSConnectionFactory


class IntegrationTestCase(SiteTestCase):
    connection_class = None

    def setUp(self):
        super(IntegrationTestCase, self).setUp()

        # Add a connection factory
        self.connection_factory = DebugHTTPSConnectionFactory(self.connection_class)
        # Register it with the site
        self.site._s3_https_connection_factory = (self.connection_factory, ())

        # Update the site's credential manager to a test one
        self.site.credentials_manager = DummyAWSCredentialsManager(self.site)

        # Remove plugins
        self.site.plugin_manager = PluginManager(self.site, [])

        # Clean up the site paths
        for path in (self.site.page_path, self.site.static_path):
            shutil.rmtree(path)
            os.mkdir(path)
