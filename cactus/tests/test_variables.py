#coding:utf-8
from cactus import Site
from cactus.tests import SiteTest


# noinspection PyUnresolvedReferences
class AbstractTestVariables(object):
    """
    Test that the context is there, but don't provide it (other tests will!)
    """
    def testSiteContext(self):
        """
        Test that site context is provided to the pages.
        """
        self.assertEqual(
            [page.source_path for page in self.site.context()['CACTUS']['pages']],
            ['error.html', 'index.html']
        )

        self.assertEqual(self.site.context()['a'], 'b')
        self.assertEqual(self.site.context()['c'], True)


class TestSiteVariables(AbstractTestVariables, SiteTest):
    """
    Test that variables passed to the site constructor are used.
    """
    def setUp(self):
        super(TestSiteVariables, self).setUp()
        self.site = Site(self.path, self.config_path, variables=['a=b', 'c'])


class TestConfigVariables(AbstractTestVariables, SiteTest):
    """
    Test that variables passed in the config file are used.
    """
    def setUp(self):
        super(TestConfigVariables, self).setUp()
        self.conf.set("variables", {"a":"b", "c":True})
        self.conf.write()

        self.site = Site(self.path, self.config_path)