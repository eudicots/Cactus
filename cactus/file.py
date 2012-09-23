import os
import codecs
import logging
import hashlib
import mime

from .utils import compressString, getURLHeaders, fileSize

class File(object):
	
	CACHE_EXPIRATION = 60 * 60 * 24 # 24 hours
	COMPRESS_TYPES = ['html', 'css', 'js', 'txt', 'xml']
	COMPRESS_MIN_SIZE = 1024 # 1kb
	
	def __init__(self, site, path):
		self.site = site
		self.path = path

		self.paths = {
			'full': os.path.join(site.path, 'build', self.path)
		}
	
	def data(self):
		if not hasattr(self, '_data'):
			f = open(self.paths['full'], 'r')
			self._data = f.read()
			f.close()
		return self._data
		
	def payload(self):
		"""
		The representation of the data that should be uploaded to the
		server. This might be compressed based on the content type and size.
		"""
		
		if not self.shouldCompress():
			return self.data()
		
		if not hasattr(self, '_compressedData'):
			self._compressedData = compressString(self.data())
		
		return self._compressedData
	
	def checksum(self):
		"""
		An amazon compatible md5 of the payload data.
		"""
		return hashlib.md5(self.payload()).hexdigest()
	
	def remoteChecksum(self):
		return getURLHeaders(self.remoteURL()).get('etag', '').strip('"')
		
	def remoteURL(self):
		return 'http://%s/%s' % (self.site.config.get('aws-bucket-website'), self.path)
	
	def extension(self):
		return os.path.splitext(self.path)[1].strip('.').lower()
		
	def shouldCompress(self):
		
		if not self.extension() in self.COMPRESS_TYPES:
			return False
		
		if len(self.data()) < self.COMPRESS_MIN_SIZE:
			return False
		
		return True
	
	def upload(self, bucket):
		
		headers = {'Cache-Control': 'max-age=%s' % self.CACHE_EXPIRATION}
		
		if self.shouldCompress():
			headers['Content-Encoding'] = 'gzip'
		
		changed = self.checksum() != self.remoteChecksum()
		
		if changed:
			key = bucket.new_key(self.path)
			mimeType = mime.guess(self.path)[0]
			if mimeType: key.content_type = mimeType
			key.set_contents_from_string(self.payload(), headers, policy='public-read')
 		
		op1 = '+' if changed else '-'
		op2 = ' (%s compressed)' % (fileSize(len(self.payload()))) if self.shouldCompress() else ''
		
		logging.info('%s %s - %s%s' % (op1, self.path, fileSize(len(self.data())), op2))
		
		return {'changed': changed, 'size': len(self.payload())}
		
		