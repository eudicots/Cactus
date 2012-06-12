import os
import codecs

class File(object):
	
	def __init__(self, site, path):
		self.site = site
		self.path = path

		self.paths = {
			'full': os.path.join(site.path, 'build', self.path)
		}
	
	def data(self):
		f = codecs.open(self.paths['full'], 'r', 'utf-8')
		data = f.read()
		f.close()
		return data
		
	def payload(self):
		"""
		The representation of the data that should be uploaded to the
		server. This might be compressed based on the content type.
		"""
	
	def checksum(self):
		"""
		An amazon compatible md5 of the payload data.
		"""