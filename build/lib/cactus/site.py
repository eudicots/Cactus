import os
import sys
import shutil
import logging
import subprocess
import webbrowser

from .config import Config
from .utils import fileList, multiMap
from .page import Page
from .listener import Listener

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
	
	def verify(self):
		"""
		Check if this path looks like a Cactus website
		"""
		for p in ['pages', 'static', 'templates']:
			if not os.path.isdir(os.path.join(self.path, p)):
				logging.info('This does not look like a cactus project (missing "%s" subfolder)', p)
				sys.exit()
	
	def bootstrap(self):
		"""
		Bootstrap a new project at a given path.
		"""
		
		# If we're running a version installed with distutils, we need to 
		# uncompress the skeleton files to the given location.
		skeletonPath = os.path.join(os.path.dirname(__file__), '..', 'skeleton.tar.gz')
		
		if os.path.exists(skeletonPath):
			os.mkdir(self.path)
			os.system('tar -zxvf "%s" -C "%s"' % (skeletonPath, self.path))
		else:
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
		multiMap = map
		multiMap(lambda p: p.build(), self.pages())
	
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

	def serve(self, browser=True, port=8000):
		"""
		Start a http server and rebuild on changes.
		"""
		self.build()
	
		logging.info('Running webserver at 0.0.0.0:%s for %s' % (port, self.paths['build']))
		logging.info('Type control-c to exit')
	
		os.chdir(self.paths['build'])
		
		def rebuild(change):
			logging.info('*** Rebuilding (%s changed)' % change)
			# self.loadExtras(force=True)
			self.build()
	
		Listener(self.path, rebuild, ignore=lambda x: '/build/' in x).run()

		import SimpleHTTPServer
		import SocketServer
		import socket

		class Server(SocketServer.ForkingMixIn, SocketServer.TCPServer):
			allow_reuse_address = True
		
		class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
			
			def send_error(self, code, message=None):
				
				if code == 404:
					self.path = '/error.html'
					return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
				
				return SimpleHTTPServer.SimpleHTTPRequestHandler.send_error(
					self, code, message=None)
		
		try:
			httpd = Server(("", port), RequestHandler)
		except socket.error, e:
			logging.info('Could not start webserver, port is in use. To use another port:')
			logging.info('  cactus serve %s' % (int(port) + 1))
			return
		
		webbrowser.open('http://127.0.0.1:%s' % port)
	
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			pass
