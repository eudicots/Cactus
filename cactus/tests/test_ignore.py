#coding:utf-8
import os
from cactus.tests import SiteTestCase


class TestIgnore(SiteTestCase):
    def test_ignore_static(self):
        with open(os.path.join(self.site.static_path, "koen.psd"), "w") as f:
            f.write("Not really a psd")

        with open(os.path.join(self.site.static_path, "koen.gif"), "w") as f:
            f.write("Not really a gif")

        self.site.config.set("ignore", ["*.psd"])
        self.site.build()

        self.assertFileDoesNotExist(os.path.join(self.site.build_path, "static", "koen.psd"))
        self.assertFileExists(os.path.join(self.site.build_path, "static", "koen.gif"))

    def test_ignore_pages(self):
        with open(os.path.join(self.site.page_path, "page.html.swp"), "w") as f:
            f.write("Not really a swap file")

        with open(os.path.join(self.site.page_path, "page.txt"), "w") as f:
            f.write("Actually a text file")

        self.site.config.set("ignore", ["*.swp"])
        self.site.build()

        self.assertFileDoesNotExist(os.path.join(self.site.build_path, "page.html.swp"))
        self.assertFileExists(os.path.join(self.site.build_path, "page.txt"))
