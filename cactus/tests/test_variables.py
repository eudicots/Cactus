#coding:utf-8
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
    def get_variables_for_test(self):
        return ['a=b', 'c']


class TestConfigVariables(AbstractTestVariables, SiteTest):
    """
    Test that variables passed in the config file are used.
    """
    def get_config_for_test(self):
        return {"variables": {"a":"b", "c":True}}