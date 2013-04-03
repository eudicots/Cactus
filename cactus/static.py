#coding:utf-8
import os
import logging
import subprocess
import shutil

class Static(object):
	def __init__(self, site, path):
		self.site = site
		self.path = path

		self.paths = {
				'full': os.path.join(self.site.path, 'static', self.path),
				'full-build': os.path.join(site.paths['build'], 'static', self.path),
				}

	def build(self):
		logging.info('Building static %s' % self.path)
		# Make sure a folder for the output path exists
		try: os.makedirs(os.path.dirname(self.paths['full-build']))
		except OSError: pass

		shutil.copy(self.paths['full'], self.paths['full-build'])
