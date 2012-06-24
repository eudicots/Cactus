import os
import re
import httplib
import urlparse
import urllib
import types
import logging

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

	try:
		from multiprocessing.pool import ThreadPool
	except ImportError:
		return map(f, items)
	
	pool = ThreadPool(workers)
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
		
	
