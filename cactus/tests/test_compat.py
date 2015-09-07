#coding:utf-8
from cactus.tests import SiteTestCase


class TestCompatibility(SiteTestCase):
    def _paths_key_exists(self, obj, old_key):
        try:
            obj.paths[old_key]
        except KeyError:
            self.fail('Old key does not exist anymore: {0}'.format(old_key))

    def test_compatibility(self):
        """
        Test that we can access the path elements the "old" way
        Just try a few of them, we're not locking this down - just testing
        """
        for old_key, new_field in (
            ('build', 'build_path'),
            ('pages', 'page_path'),
        ):
            self.assertEqual(self.site.paths[old_key], getattr(self.site, new_field))

    def test_site_paths_keys_exist(self):
        for old_key in ('build', 'pages', 'plugins', 'templates', 'static', 'script'):
            self._paths_key_exists(self.site, old_key)

    def test_page_paths_keys_exist(self):
        page = self.site.pages()[0]

        for old_key in ('full', 'full-build'):
            self._paths_key_exists(page, old_key)

    def test_page_path_attr(self):
        page = self.site.pages()[0]
        self.assertEqual(page.source_path, page.path)

    def test_page_paths_keys_exist_in_static(self):
        static = self.site.static()[0]

        for old_key in ('full', 'full-build'):
            self._paths_key_exists(static, old_key)
