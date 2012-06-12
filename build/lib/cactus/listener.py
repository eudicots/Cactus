import os
import sys
import time
import thread

from .utils import fileList

class Listener(object):
	
	def __init__(self, path, f, delay=.5, ignore=None):
		self.path = path
		self.f = f
		self.delay = delay
		self.ignore = ignore
		self.current = None
	
	def checksum(self, path):
		
		total = 0
		
		for f in fileList(path):
			if f.startswith('.'):
				continue
			if self.ignore and self.ignore(f) == True:
				continue
			total += int(os.stat(f).st_mtime)
		
		return total
	
	def run(self):
		# self._run()
		t = thread.start_new_thread(self._run, ())
		
	def _run(self):
		
		self.current = self.checksum(self.path)
		
		while True:
			
			s = self.checksum(self.path)
	
			if s != self.current:
				self.current = s
				self.f(self.path)
			
			time.sleep(self.delay)