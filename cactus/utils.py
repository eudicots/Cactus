import os
import re
import httplib
import urlparse
import urllib
import urllib2
import types
import logging
import time
import fnmatch
import multiprocessing.pool

from functools import partial

def fileList(paths, relative=False, folders=False):
	"""
	Generate a recursive list of files from a given path.
	"""
	
	if not type(paths) == types.ListType:
		paths = [paths]
	
	files = []
	
	for path in paths:	
		for fileName in os.listdir(path):
		
			if fileName.startswith('.'):
				continue
		
			filePath = os.path.join(path, fileName)
		
			if os.path.isdir(filePath):
				if folders:
					files.append(filePath)
				files += fileList(filePath)
			else:
				files.append(filePath)
	
		if relative:
			files = map(lambda x: x[len(path)+1:], files)
		
	return files

def multiMap(f, items, workers=8):
	pool = multiprocessing.pool.ThreadPool(workers)
	return pool.map(f, items)
	
def getpassword(service, account):
	
	def decode_hex(s):
		s = eval('"' + re.sub(r"(..)", r"\x\1", s) + '"')
		if "" in s: s = s[:s.index("")]
		return s

	cmd = ' '.join([
		"/usr/bin/security",
		" find-generic-password",
		"-g -s '%s' -a '%s'" % (service, account),
		"2>&1 >/dev/null"
	])
	p = os.popen(cmd)
	s = p.read()
	p.close()
	m = re.match(r"password: (?:0x([0-9A-F]+)\s*)?\"(.*)\"$", s)
	if m:
		hexform, stringform = m.groups()
		if hexform: 
			return decode_hex(hexform)
		else:
			return stringform

def setpassword(service, account, password):
	cmd = 'security add-generic-password -U -a %s -s %s -p %s' % (account, service, password)
	p = os.popen(cmd)
	s = p.read()
	p.close()

def compressString(s):
	"""Gzip a given string."""
	import cStringIO, gzip

	# Nasty monkeypatch to avoid gzip changing every time
	class FakeTime:
		def time(self):
			return 1111111111.111

	gzip.time = FakeTime()
	
	zbuf = cStringIO.StringIO()
	zfile = gzip.GzipFile(mode='wb', compresslevel=9, fileobj=zbuf)
	zfile.write(s)
	zfile.close()
	return zbuf.getvalue()


def getURLHeaders(url):
	
	url = urlparse.urlparse(url)
	
	conn = httplib.HTTPConnection(url.netloc)
	conn.request('HEAD', urllib.quote(url.path))

	response = conn.getresponse()

	return dict(response.getheaders())


def fileSize(num):
	for x in ['b','kb','mb','gb','tb']:
		if num < 1024.0:
			return "%.0f%s" % (num, x)
		num /= 1024.0


def parseValues(data, splitChar=':'):
	"""
	Values like
	
	name: koen
	age: 29
	
	will be converted in a dict: {'name': 'koen', 'age': '29'}
	"""

	values = {}
	lines  = data.splitlines()
	
	if not lines:
		return {}, ''
	
	for i in xrange(len(lines)):

		line = lines[i]

		if not line:
			continue
		
		elif splitChar in line:
			line = line.split(splitChar)
			values[line[0].strip()] = (splitChar.join(line[1:])).strip()
		
		else:
			break
	
	return values, '\n'.join(lines[i:])
		
def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
	def deco_retry(f):
		def f_retry(*args, **kwargs):
			mtries, mdelay = tries, delay
			try_one_last_time = True
			while mtries > 1:
				try:
					return f(*args, **kwargs)
					try_one_last_time = False
					break
				except ExceptionToCheck, e:
					logging.warning("%s, Retrying in %.1f seconds..." % (str(e), mdelay))
					time.sleep(mdelay)
					mtries -= 1
					mdelay *= backoff
			if try_one_last_time:
				return f(*args, **kwargs)
			return
		return f_retry  # true decorator
	return deco_retry

class memoize(object):
	def __init__(self, func):
		self.func = func
	def __get__(self, obj, objtype=None):
		if obj is None:
			return self.func
		return partial(self, obj)
	def __call__(self, *args, **kw):
		obj = args[0]
		try:
			cache = obj.__cache
		except AttributeError:
			cache = obj.__cache = {}
		key = (self.func, args[1:], frozenset(kw.items()))
		try:
			res = cache[key]
		except KeyError:
			res = cache[key] = self.func(*args, **kw)
		return res

def internetWorking():

	def check(url):
		try:
			response = urllib2.urlopen(url, timeout=1)
			return True
		except urllib2.URLError as err: pass
		return False

	return True in multiMap(check, [
		'http://www.google.com', 
		'http://www.apple.com'])


def filterPaths(paths, patterns):

	def ignorePath(path):

		fileName = os.path.basename(path)
		
		for pattern in patterns:
			if fnmatch.fnmatch(fileName, pattern):
				return True
		return False
			
	return filter(lambda x: not ignorePath(x), paths)
