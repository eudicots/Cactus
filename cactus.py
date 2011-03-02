#!/usr/bin/env python
# encoding: utf-8
"""
cactus.py

Created by Koen Bok on 2011-02-26.
Copyright (c) 2011 Sofa BV. All rights reserved.
"""

import sys
import os
import re
import codecs
import shutil
import baker
import subprocess
import webbrowser
import time
import thread
import simplejson as json

from distutils import dir_util

from django.template import Template, Context
from django.template import loader as templateLoader


###############################################################
### UTILITIES

class Config(object):
	def __init__(self, path):
		self.path = path
		self.load()
	
	def get(self, key):
		return self._data.get(key, None)
	
	def set(self, key, value):
		self._data[key] = value
	
	def load(self):
		try:
			self._data = json.load(open(self.path, 'r'))
		except:
			self._data = {}
	
	def write(self):
		json.dump(self._data, open(self.path, 'w'), sort_keys=True, indent=4)
		

def fileList(path):
	
	files = []
	
	for fileName in os.listdir(path):
		
		if fileName.startswith('.'):
			continue
		
		filePath = os.path.join(path, fileName)
		
		if os.path.isdir(filePath):
			files += fileList(filePath)
		else:
			files.append(filePath)
		
	return files


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
	zbuf = cStringIO.StringIO()
	zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
	zfile.write(s)
	zfile.close()
	return zbuf.getvalue()


###############################################################
### COMMAND LINE FUNCTIONS

@baker.command
def init(path):
	"""
	Generate new site at path
	"""
	
	if os.path.exists(path):
		print 'Error: path already exists: %s' % path
		return
	
	os.mkdir(path)
	
	# Generate basic structure
	for d in ['templates', 'static', 'static/css', 'static/js', 'static/images', 'pages', 'build', 'extras']:
		os.mkdir(os.path.join(path, d))
	
	# Generate some default files
	open(os.path.join(path, 'templates', 'base.html'), 'w').write(templateFile)
	open(os.path.join(path, 'pages', 'index.html'), 'w').write(indexFile)
	open(os.path.join(path, 'extras', 'contexts.py'), 'w').write(contextsFile)
	open(os.path.join(path, 'extras', 'templatetags.py'), 'w').write("")
	
	print 'New project generated at %s' % path


@baker.command
def build(path):
	"""
	Rebuild site at path
	"""
	# Set up django
	
	templatePath = os.path.join(path, 'templates')
	pagesPath = os.path.join(path, 'pages')
	
	staticPath = os.path.join(path, 'static')
	buildPath = os.path.join(path, 'build')
	
	try:
		from django.conf import settings
		settings.configure(TEMPLATE_DIRS=[templatePath, pagesPath])
	except:
		pass
	
	# Load custom python code
	
	sys.path.append(os.path.join(path, 'extras'))
	import contexts
	import templatetags

	
	# Make sure the build path exists
	if not os.path.exists(buildPath):
		os.mkdir(buildPath)
	
	def buildPage(path):
		
		print "Building %s" % (path)
		
		outputPath = os.path.join(buildPath, path)
		
		try:
			os.makedirs(os.path.dirname(outputPath))
		except OSError:
			pass
		
		t = templateLoader.get_template(path)
		f = codecs.open(outputPath, 'w', 'utf8')
		
		prefix = '/'.join(['..' for i in xrange(len(path.split('/')) - 1)])
		
		context = {
			'MEDIA_PATH': os.path.join(prefix, 'static'),
			'ROOT_PATH': prefix,
		}
		
		context.update(contexts.context(path))
		
		f.write(t.render(Context(context)))
		f.close()
	
	map(buildPage, [f.replace('%s/' % pagesPath, '') for f in fileList(pagesPath)])
	
	dir_util.copy_tree(staticPath, os.path.join(buildPath, 'static'), verbose=1)

@baker.command
def serve(path, port=8000, browser=True):
	
	buildPath = os.path.join(path, 'build')
	
	# See if the project ever got built
	if not os.path.isdir(buildPath) or len(fileList(buildPath)) == 0:
		build(path)
	
	print 'Running webserver at 0.0.0.0:%s for %s' % (port, buildPath)
	print 'Type control-c to exit'
	
	# Start the webserver in a subprocess
	os.chdir(buildPath)
		
	def rebuild(change):
		print '*** Rebuilding (%s changed)' % change
		build(path)
	
	Listener(path, rebuild, ignore=lambda x: '/build/' in x).run()

	import SimpleHTTPServer
	import SocketServer
	
	SocketServer.ThreadingTCPServer.allow_reuse_address = True
	
	httpd = SocketServer.ThreadingTCPServer(("", port), 
		SimpleHTTPServer.SimpleHTTPRequestHandler)
	
	if browser is True:
		print 'Opening web browser (disable by adding --browser=no to command)'
		webbrowser.open('http://127.0.0.1:%s' % port)
	
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass


@baker.command
def deploy(path, compress='html,htm,css,js,txt'):

	import boto
	import getpass
	import mimetypes
	
	build(path)
	buildPath = os.path.join(path, 'build')
	
	config = Config(os.path.join(path, 'config.json'))
	
	awsAccessKey = config.get('aws-access-key') or raw_input('Amazon access key: ')
	awsSecretKey = getpassword('aws', awsAccessKey) or getpass.getpass('Amazon secret access key: ')
	
	connection = boto.connect_s3(awsAccessKey.strip(), awsSecretKey.strip())
	
	try:
		buckets = connection.get_all_buckets()
	except:
		print 'Invalid login credentials, please try again...'
		return
	
	config.set('aws-access-key', awsAccessKey)
	config.write()
	
	setpassword('aws', awsAccessKey, awsSecretKey)
	
	awsBucketName = config.get('aws-bucket-name') or raw_input('S3 bucket name: ')
	
	if awsBucketName not in [b.name for b in buckets]:
		if raw_input('Bucket does not exist, create it? (y/n): ') == 'y':
			awsBucket = connection.create_bucket(awsBucketName, policy='public-read')
			awsBucket.configure_website('index.html', 'error.html')
			config.set('aws-bucket-website', awsBucket.get_website_endpoint())
			config.set('aws-bucket-name', awsBucketName)
			config.write()
			
			print 'Bucket %s was created with website endpoint %s' % (config.get('aws-bucket-name'), config.get('aws-bucket-website'))
			print 'You can learn more about s3 (like pointing to your own domain) here: https://github.com/koenbok/Cactus'
			
		else: return
	else:
		for b in buckets:
			if b.name == awsBucketName:
				awsBucket = b
	
	print 'Uploading site to bucket %s' % awsBucketName
	
	def uploadFile(path):
		
		relativePath = path.replace('%s/' % buildPath, '')
		headers = {'Cache-Control': 'max-age %d' % (3600 * 24 * 365)}
		
		print '* %s...' % relativePath
		
		data = open(os.path.join(buildPath, path), 'r').read()
		
		if len(data) > 1024 and os.path.splitext(relativePath)[1].strip('.').lower() in compress.split(','):
			data = compressString(data)
			headers['Content-Encoding'] = 'gzip'
		
		key = awsBucket.new_key(relativePath)
		key.content_type = mimetypes.guess_type(path)[0]
		key.set_contents_from_string(data, headers, policy='public-read')
		
	map(uploadFile, fileList(buildPath))
	
	print
	print 'Upload done: http://%s' % config.get('aws-bucket-website')
	print


###############################################################
### TEMPLATES

templateFile = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>Welcome</title>
</head>
<body>
	{% block content %}
	Main content
	{% endblock %}
</body>
</html>
"""

indexFile = """{% extends "base.html" %}
{% block content %}
Welcome to Cactus!
{% endblock %}
"""

contextsFile = """def context(url):
	return {}
"""

baker.run()
