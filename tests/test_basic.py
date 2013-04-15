import os
import shutil
import codecs
import unittest
import tempfile

import django.conf

from cactus import Site
from cactus.utils import fileList, bootstrap


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
	return readFile(os.path.join('tests', 'data', name))



class SimpleTest(unittest.TestCase):
	
	def setUp(self):
		self.test_dir = tempfile.mkdtemp()
		self.path = os.path.join(self.test_dir, 'test')

		self.clear_django_settings()

		bootstrap(self.path)
		self.site = Site(self.path, os.path.join(self.path, 'config.json'), variables = ['a=b', 'c'])


	def clear_django_settings(self):
		django.conf.settings._wrapped = django.conf.empty


	def tearDown(self):
		shutil.rmtree(self.test_dir)


	def testBootstrap(self):
		self.assertEqual(
			fileList(self.path, relative=True),
			fileList("skeleton", relative=True), 
		)


	def testBuild(self):
		self.site.build()
		
		# Make sure we build to .build and not build
		self.assertEqual(os.path.exists(os.path.join(self.path, 'build')), False)
		
		self.assertEqual(fileList(os.path.join(self.path, '.build'), relative=True), [
			'error.html',
			'index.html',
			'robots.txt',
			'sitemap.xml',
			self.site.get_path_for_static('static/css/style.css'),
			self.site.get_path_for_static('static/js/main.js'),
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
			[page.path for page in self.site.context()['CACTUS']['pages']],
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
			if page.path == 'koenpage.html':
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
