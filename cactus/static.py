#coding:utf-8
import os
import logging
import subprocess
import shutil
import hashlib

FINGERPRINT_EXTENSIONS = ("js", "css")

def calculate_file_checksum(path):
	"""
	Calculate the MD5 sum for a file (needs to fit in memory)
	"""
	with open(path) as f:
		return hashlib.md5(f.read()).hexdigest()


class Static(object):
	"""
	A static resource in the repo
	"""

	def __init__(self, site, path):
		self.site = site
		self.src_path = os.path.join('static', path)

		full_path = os.path.join(self.site.path, self.src_path)
		checksum = calculate_file_checksum(full_path)

		prefix, _filename = os.path.split(self.src_path)
		filename, extension = os.path.basename(full_path).rsplit('.', 1)

		assert extension, "No extension for file?! {0}".format(full_path)


		if extension in FINGERPRINT_EXTENSIONS:
			new_filename = "{0}.{1}.{2}".format(filename, checksum, extension)
		else:
			new_filename = _filename


		self.build_path = os.path.join(prefix, new_filename)

		self.paths = {
			'full': full_path,
			'full-build': os.path.join(site.paths['build'], self.build_path),
		}


	def build(self):
		logging.info('Building {0} --> {1}'.format(self.src_path, self.build_path))

		try: os.makedirs(os.path.dirname(self.paths['full-build']))
		except OSError: pass

		if self.site.optimize:
			try:
				if self.src_path.endswith('.js'):
					logging.info('Compiling (closure): %s' % self.src_path)
					subprocess.call([
						'closure-compiler',
						'--js', self.paths['full'],
						'--js_output_file', self.paths['full-build'],
						'--compilation_level', 'SIMPLE_OPTIMIZATIONS'
					])

				elif self.src_path.endswith('.css'):
					logging.info('Minifying (yui) %s' % self.src_path)
					subprocess.call([
						'yuicompressor',
						'--type', 'css',
						'-o', self.paths['full-build'],
						self.paths['full']
					])
			except OSError:
				logging.warning('Aborted optimization: missing external.')
			else:
				return

		shutil.copy(self.paths['full'], self.paths['full-build'])


	def __repr__(self):
		return '<Static: {0}>'.format(self.src_path)
