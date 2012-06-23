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
	
		self.assertEqual(fileList(os.path.join(TEST_PATH, 'build'), relative=True), [
			'error.html',
			'index.html',
			'robots.txt',
			'sitemap.xml'])
	
	
	def testRenderPage(self):
		
		# Create a new page called test.html and see if it get rendered
		
		writeFile(
			os.path.join(TEST_PATH, 'pages', 'test.html'),
			mockFile('test-in.html')
		)
		
		self.site.build()
		
		print os.path.join(TEST_PATH, 'build', 'test.html')
		
		self.assertEqual(
			readFile(os.path.join(TEST_PATH, 'build', 'test.html')),
			mockFile('test-out.html')
		)
# 	
# 	def testSiteContext(self):
# 		
# 		self.assertEqual(
# 			[page.path for page in self.site.context()['CACTUS']['pages']],
# 			['error.html', 'index.html', 'robots.txt', 'sitemap.xml', 'test.html']
# 		)
# 	
# 	def testPageContext(self):
# 
# 		writeFile(
# 			os.path.join(TEST_PATH, 'pages', 'about.html'),
# 			"""
# name: Koen Bok
# age: 29
# {% extends "base.html" %}
# {% block content %}
# I am {{ name }} and {{ age }} years old.
# {% endblock %}'
# """)
# 
# 	
