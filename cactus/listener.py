import os
import sys
import time
import thread

from .utils import fileList
from .utils import retry

class Listener(object):
	
	def __init__(self, path, f, delay=.5, ignore=None):
		self.path = path
		self.f = f
		self.delay = delay
		self.ignore = ignore
		self._pause = False
		self._checksums = {}
	
	def checksums(self):
		checksumMap = {}
		
		for f in fileList(self.path):
			
			if f.startswith('.'):
				continue
			
			if self.ignore and self.ignore(f) == True:
				continue
			
			try:
				checksumMap[f] = int(os.stat(f).st_mtime)
			except OSError, e:
				continue

		return checksumMap
	
	def run(self):
		# self._loop()
		t = thread.start_new_thread(self._loop, ())
	
	def pause(self):
		self._pause = True
	
	def resume(self):
		self._checksums = self.checksums()
		self._pause = False
	
	def _loop(self):
		
		self._checksums = self.checksums()
		
		while True and self._pause == False:
			self._run()
	
	@retry(Exception, tries=5, delay=0.5)
	def _run(self):
			
		oldChecksums = self._checksums
		newChecksums = self.checksums()
		
		result = {
			'added': [],
			'deleted': [],
			'changed': [],
		}
		
		for k, v in oldChecksums.iteritems():
			if k not in newChecksums:
				result['deleted'].append(k)
			elif v != newChecksums[k]:
				result['changed'].append(k)
		
		for k, v in newChecksums.iteritems():
			if k not in oldChecksums:
				result['added'].append(k)
			
		result['any'] = result['added'] + result['deleted'] + result['changed']
		
		if result['any']:
			self._checksums = newChecksums
			self.f(result)
		
		time.sleep(self.delay)