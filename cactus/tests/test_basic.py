import os
import codecs

from cactus.site import Site
from cactus.config import Config
from cactus.utils import fileList
from cactus.tests import BaseTest


def readFile(path):
    f = codecs.open(path, 'r', 'utf8')
    d = f.read()
    f.close()
    return d


def writeFile(path, data):
    f = codecs.open(path, 'w', 'utf8')
    f.write(data)
    f.close()


def mockFile(name):
    return readFile(os.path.join('cactus', 'tests', 'data', name))


class TestBootstrap(BaseTest):
    def testBootstrap(self):
        self.assertEqual(
            fileList(self.path, relative = True),
            fileList("skeleton", relative = True),
        )


class TestSite(BaseTest):
    def setUp(self):
        super(TestSite, self).setUp()

        config_path = os.path.join(self.path, 'config.json')
        conf = Config(config_path)
        conf.set('site-url', 'http://example.com/')
        conf.write()

        self.site = Site(self.path, config_path, variables = ['a=b', 'c'])

    def testBuild(self):
        self.site.build()

        # Make sure we build to .build and not build
        self.assertEqual(os.path.exists(os.path.join(self.path, 'build')), False)

        self.assertEqual(fileList(os.path.join(self.path, '.build'), relative=True), [
            'error.html',
            'index.html',
            'robots.txt',
            'sitemap.xml',
            self.site.get_path_for_static('/static/css/style.css')[1:],  # Strip the initial /
            self.site.get_path_for_static('/static/js/main.js')[1:],  # Strip the initial /
        ])

    def testRenderPage(self):

        # Create a new page called test.html and see if it get rendered

        writeFile(
            os.path.join(self.path, 'pages', 'test.html'),
            mockFile('test-in.html')
        )

        self.site.build()

        self.assertEqual(
            readFile(os.path.join(self.path, '.build', 'test.html')),
            mockFile('test-out.html')
        )

    def testSiteContext(self):
        self.assertEqual(
            [page.source_path for page in self.site.context()['CACTUS']['pages']],
            ['error.html', 'index.html']
        )

        self.assertEqual(self.site.context()['a'], 'b')
        self.assertEqual(self.site.context()['c'], True)

    def testPageContext(self):

        writeFile(
            os.path.join(self.path, 'pages', 'koenpage.html'),
            mockFile('koenpage-in.html')
        )

        for page in self.site.context()['CACTUS']['pages']:
            if page.source_path == 'koenpage.html':
                context = page.context()
                self.assertEqual(context['name'], 'Koen Bok')
                self.assertEqual(context['age'], '29')

        self.site.build()

        self.assertEqual(
            readFile(os.path.join(self.path, '.build', 'koenpage.html')),
            mockFile('koenpage-out.html')
        )

    def testStaticLoader(self):
        static = '/static/css/style.css'
        page = "{%% static '%s' %%}" % static

        writeFile(
            os.path.join(self.path, 'pages', 'staticpage.html'),
            page
        )

        self.site.build()

        self.assertEqual(
            readFile(os.path.join(self.path, '.build', 'staticpage.html')),
            self.site.get_path_for_static(static)
        )
