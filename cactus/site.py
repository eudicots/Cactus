import os
import shutil
import logging

from .config import Config
from .utils import fileList
from .page import Page

class Site(object):
	
	def __init__(self, path):
		
		self.path = path

		self.paths = {
			'config': os.path.join(path, 'config.json'),
			'build': os.path.join(path, 'build'),
			'pages': os.path.join(path, 'pages'),
			'templates': os.path.join(path, 'templates'),
			'extras': os.path.join(path, 'extras'),
			'static': os.path.join(path, 'static'),
			'script': os.path.join(os.getcwd(), __file__)
		}
		
		self.config = Config(self.paths['config'])
	
	def setup(self):
		"""
		Configure django to use both our template and pages folder as locations
		to look for included templates.
		"""
		try:
			from django.conf import settings
			settings.configure(TEMPLATE_DIRS=[self.paths['templates'], self.paths['pages']])
		except:
			pass
	
	def bootstrap(self):
		"""
		Bootstrap a new project at a given path.
		"""
		skeletonPath = os.path.join(os.path.dirname(__file__), 'skeleton')
		
		shutil.copytree(skeletonPath, self.path)
	
		logging.info('New project generated at %s', self.path)

	def context(self):
		"""
		Base context for the site.
		"""
		return {}

	def build(self):
		"""
		Generate fresh site from templates.
		"""
		
		# Set up django settings
		self.setup()
		
		# Make sure the build path exists
		if not os.path.exists(self.paths['build']):
			os.mkdir(self.paths['build'])
		
		# Copy the static files
		self.buildStatic()
		
		# Render the pages to their output files
		map(lambda p: p.build(), self.pages())
	
	def buildStatic(self):
		"""
		Move static files to build folder. To be fast we symlink it for now,
		but we should actually copy these files in the future.
		"""
		staticBuildPath = os.path.join(self.paths['build'], 'static')
		
		# If there is a folder, replace it with a symlink
		if os.path.lexists(staticBuildPath) and not os.path.exists(staticBuildPath):
			os.remove(staticBuildPath)
		
		if not os.path.lexists(staticBuildPath):
			os.symlink(self.paths['static'], staticBuildPath)
	
	def upload(self):
		"""
		Upload the site to the server.
		"""
	
	def pages(self):
		"""
		List of pages.
		"""
		return [Page(self, p) for p in fileList(self.paths['pages'], relative=True)]

	def files(self):
		"""
		List of build files.
		"""
		return [File(self, p) for p in fileList(self.paths['build'])]
