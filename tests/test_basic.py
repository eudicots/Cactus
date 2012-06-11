import os
import shutil
import codecs
import unittest

from cactus import Site
from cactus.utils import fileList

TEST_PATH = '/tmp/www.testcactus.com'

class SimpleTest(unittest.TestCase):
	
	@classmethod
	def setUpClass(cls):
		if os.path.exists(TEST_PATH):
			shutil.rmtree(TEST_PATH)

		cls.site = Site(TEST_PATH)
	
	def testBootstrap(self):
		
		self.site.bootstrap()
		
		self.assertEqual(fileList(TEST_PATH, relative=True), [
			'pages/error.html',
			'pages/index.html',
			'pages/robots.txt',
			'pages/sitemap.xml',
			'plugins/__init__.py',
			'plugins/render.py',
			'plugins/templatetags.py',
			'plugins/version.py',
			'templates/base.html'])


	def testBuild(self):
		
		self.site.build()

		self.assertEqual(fileList(os.path.join(TEST_PATH, 'build'), relative=True), [
			'error.html',
			'index.html',
			'robots.txt',
			'sitemap.xml'])
