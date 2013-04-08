import os
import shutil
import codecs
import unittest

from cactus import Site
from cactus.utils import fileList

TEST_PATH = '/tmp/www.testcactus.com'


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
	
	@classmethod
	def setUpClass(cls):
		if os.path.exists(TEST_PATH):
			shutil.rmtree(TEST_PATH)

		cls.site = Site(TEST_PATH)
	
	def testBootstrap(self):
		
		self.site.bootstrap()
		
		self.assertEqual(
			fileList(TEST_PATH, relative=True), 
			fileList("skeleton", relative=True), 
		)


	def testBuild(self):
		
		self.site.build()
		
		# Make sure we build to .build and not build
		self.assertEqual(os.path.exists(os.path.join(TEST_PATH, 'build')), False)
		
		self.assertEqual(fileList(os.path.join(TEST_PATH, '.build'), relative=True), [
			'error.html',
			'index.html',
			'robots.txt',
			'sitemap.xml',
			'static/css/style.css',
			'static/js/main.js'
		])
	
	#def testRenderPage(self):
		
		# Create a new page called test.html and see if it get rendered
		
		writeFile(
			os.path.join(TEST_PATH, 'pages', 'test.html'),
			mockFile('test-in.html')
		)
		
		self.site.build()
		
		self.assertEqual(
			readFile(os.path.join(TEST_PATH, '.build', 'test.html')),
			mockFile('test-out.html')
		)
	
	#def testSiteContext(self):
		
		self.assertEqual(
			[page.path for page in self.site.context()['CACTUS']['pages']],
			['error.html', 'index.html', 'test.html']
		)
	
	#def testPageContext(self):

		writeFile(
			os.path.join(TEST_PATH, 'pages', 'koenpage.html'),
			mockFile('koenpage-in.html')
		)
		
		for page in self.site.context()['CACTUS']['pages']:
			if page.path == 'koenpage.html':
				context = page.context()
				self.assertEqual(context['name'], 'Koen Bok')
				self.assertEqual(context['age'], '29')

		self.site.build()
		
		self.assertEqual(
			readFile(os.path.join(TEST_PATH, '.build', 'koenpage.html')),
			mockFile('koenpage-out.html')
		)
	
	##def testIgnoreFiles
	
		writeFile(os.path.join(TEST_PATH, 'pages', 'koen.psd'), "Not really a psd")
		
		self.site.config.set("ignore", ["*.psd"])
		
		self.site.config.write()
		self.site.config.load()
		
		self.site.build()

		self.assertEqual(os.path.exists(os.path.join(TEST_PATH, '.build', 'koen.psd')), False)

	
