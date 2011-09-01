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
import commands
import webbrowser
import traceback
import time
import thread
import threading
import simplejson as json
# import threadpool
import logging
import boto
import getpass
import mimetypes
import httplib
import urlparse
import hashlib
import socket
import subprocess

from distutils import dir_util

from django.template import Template, Context
from django.template import loader as templateLoader

try:
	from xml.etree.ElementTree import fromstring, tostring
except ImportError:
	from elementtree.ElementTree import fromstring, tostring


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

def getError(data):
	
	tree = fromstring(data)
	code = tree.find('.//Code/').text
	msg  = tree.find('.//Message/').text
	
	return '%s: %s' % (code, msg)

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

	# Nasty monkeypatch to avoid gzip changing every time
	class FakeTime:
		def time(self):
			return 1111111111.111

	gzip.time = FakeTime()
	
	zbuf = cStringIO.StringIO()
	zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
	zfile.write(s)
	zfile.close()
	return zbuf.getvalue()

def getURLHeaders(url):
	
	url = urlparse.urlparse(url)
	
	conn = httplib.HTTPConnection(url.netloc)
	conn.request('HEAD', url.path)

	response = conn.getresponse()

	return dict(response.getheaders())


class Site(object):
	
	def __init__(self, path, workers=8):
		
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
		self.workers = workers
		
		self.compress = 'html,htm,css,js,txt'
		self._logLock = threading.Lock()
		self.pool = None
		
	def log(self, msg):
		with self._logLock:
			print msg
	
	def loadExtras(self, force=False):
		
		# sys.path.append(self.paths['extras'])
		
		if force:
			for m in ['render', 'templatetags', 'hooks']:
				if m in sys.modules:
					del sys.modules[m]
		
		from extras import render
		from extras import templatetags
		from extras import hooks
		
		from django.template.loader import add_to_builtins
		add_to_builtins('extras.templatetags')
	
		global render, templatetags, hooks
	
	def map(self, f, items):
		
		import threadpool
		
		pool = threadpool.ThreadPool(self.workers)
		requests = threadpool.makeRequests(f, items)
		
		[pool.putRequest(req) for req in requests]
		pool.wait()
		del pool
		
	def execHook(self, name):
		
		self.loadExtras()
		hook = getattr(hooks, name, None)
		
		if callable(hook):
			hook(self.path, self.config)
		
	def create(self):
		"""
		Generate new site skeleton at given path
		"""
		
		if os.path.exists(self.path):
			if raw_input('Path %s exists, move aside (y/n): ' % self.path) == 'y':
				os.rename(self.path, '%s.%s.moved' % (self.path, int(time.time())))
			else:
				return
		
		os.mkdir(self.path)
	
		# Generate basic structure
		for d in ['templates', 'static', 'static/css', 'static/js', 'static/images', 'pages', 'build', 'extras']:
			os.mkdir(os.path.join(self.path, d))
	
		# Generate some default files
		open(os.path.join(self.path, 'templates', 'base.html'), 'w').write(templateFile)
		open(os.path.join(self.path, 'pages', 'index.html'), 'w').write(indexFile)
		open(os.path.join(self.path, 'pages', 'error.html'), 'w').write(errorFile)
		open(os.path.join(self.path, 'pages', 'sitemap.xml'), 'w').write(sitemapFile)
		open(os.path.join(self.path, 'pages', 'robots.txt'), 'w').write(robotsFile)
		open(os.path.join(self.path, 'extras', 'render.py'), 'w').write(renderFile)
		open(os.path.join(self.path, 'extras', 'hooks.py'), 'w').write(hooksFile)
		open(os.path.join(self.path, 'extras', 'templatetags.py'), 'w').write("")
		open(os.path.join(self.path, 'extras', '__init__.py'), 'w').write("")
	
		self.log('New project generated at %s' % self.path)

	def buildPage(self, path):
		
		outputPath = os.path.join(self.paths['build'], path)
	
		try:
			os.makedirs(os.path.dirname(outputPath))
		except OSError:
			pass
		
		f = codecs.open(os.path.join(self.paths['pages'], path), 'r', 'utf8')
		source = f.read()
		f.close()
		
		pageContext, data = render.process(path, source)
		
		t = Template(data)
		f = codecs.open(outputPath, 'w', 'utf8')
		
		prefix = '/'.join(['..' for i in xrange(len(path.split('/')) - 1)])
	
		context = {
			'STATIC_URL': os.path.join(prefix, 'static'),
			'ROOT_URL': prefix,
			'CACTUS': {
				'path': path,
				'pages': self._pages
			}
		}
	
		context.update(pageContext)
	
		f.write(t.render(Context(context)))
		f.close()
		
		self.log("  * Built %s" % (path))
	
	def build(self, clean=False):
				
		self.execHook('preBuild')
		
		if clean and os.path.exists(self.paths['build']):
			shutil.rmtree(self.paths['build'])
		
		# Load and setup django
		try:
			from django.conf import settings
			settings.configure(TEMPLATE_DIRS=[self.paths['templates'], self.paths['pages']])
		except:
			pass
	
		# Make sure the build path exists
		if not os.path.exists(self.paths['build']):
			os.mkdir(self.paths['build'])
		
		pages = [f.replace('%s/' % self.paths['pages'], '') for f in fileList(self.paths['pages'])]
		self._pages = []
		
		for p in pages:
			
			if not p.endswith('.html'):
				continue
			
			if p == 'error.html':
				continue
			
			if p.endswith('/index.html'):
				p = p.replace('index.html', '')
			
			if p == 'index.html':
				p = '/'
			
			self._pages.append(p)
	
		# self.map(self.buildPage, pages)
		map(self.buildPage, pages)
		
		self.log("Copying static files... %s" % (self.paths['static']))
		dir_util.copy_tree(self.paths['static'], os.path.join(self.paths['build'], 'static'), verbose=1)
		
		# if not os.path.exists(os.path.join(self.paths['build'], 'static')):
		# 	os.symlink(self.paths['static'], os.path.join(self.paths['build'], 'static'))
	
		self.execHook('postBuild')
	
	def serve(self, browser=True, port=8000):
	
		self.build()
	
		self.log('Running webserver at 0.0.0.0:%s for %s' % (port, self.paths['build']))
		self.log('Type control-c to exit')
	
		os.chdir(self.paths['build'])
		
		def rebuild(change):
					
			self.log('*** Rebuilding (%s changed)' % change)
			self.loadExtras(force=True)
			self.build()
	
		Listener(self.path, rebuild, ignore=lambda x: '/build/' in x).run()

		import SimpleHTTPServer
		import SocketServer
		
		# server = SocketServer.ThreadingTCPServer
		server = SocketServer.TCPServer
		
		server.allow_reuse_address = True
		
		class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
						
			def send_error(self, code, message=None):
				
				if code == 404:
					self.path = '/error.html'
					return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
				
				return SimpleHTTPServer.SimpleHTTPRequestHandler.send_error(self, code, message=None)
		
		try:
			httpd = server(("", port), RequestHandler)
		except socket.error, e:
			self.log('Could not start webserver. Are you running another one on the same port?')
			return
		
		# if browser is True:
		# 	print 'Opening web browser (disable by adding --browser=no to command)'
		webbrowser.open('http://127.0.0.1:%s' % port)
	
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			pass

	def uploadFile(self, path):
		
		awsBucket =  self.awsBucket
		
		relativePath = path.replace('%s/' % self.paths['build'], '')
		headers = {'Cache-Control': 'max-age %d' % (3600 * 24 * 365)}
	
		data = open(os.path.join(self.paths['build'], path), 'r').read()
		gzip = (len(data) > 1024 and os.path.splitext(relativePath)[1].strip('.').lower() in self.compress.split(','))
		
		if gzip:
			data = compressString(data)
			headers['Content-Encoding'] = 'gzip'
		
		if self.config.get('aws-bucket-website'):
			
			url = 'http://%s/%s' % (self.config.get('aws-bucket-website'), relativePath)
			dataHash = hashlib.md5(data).hexdigest()
			remoteEtag = getURLHeaders(url).get('etag', '').strip('"')
			
			if remoteEtag == dataHash:
				self.log('  = %s %s bytes%s (unchanged)...' % (relativePath, len(data), ' (gzip)' if gzip else ''))
				return
		
		key = awsBucket.new_key(relativePath)
		key.content_type = mimetypes.guess_type(path)[0]
		key.set_contents_from_string(data, headers, policy='public-read')
		
		self.changedFilesAtLastDeploy.append(relativePath)
		
		self.log('  + %s %s bytes%s...' % (relativePath, len(data), ' (gzip)' if gzip else ''))

	def deploy(self):
	
		self.build(clean=True)
		self.execHook('preDeploy')
	
		awsAccessKey = self.config.get('aws-access-key') or raw_input('Amazon access key (http://goo.gl/5OgV8): ').strip()
		awsSecretKey = getpassword('aws', awsAccessKey) or getpass._raw_input('Amazon secret access key: ').strip()
	
		connection = boto.connect_s3(awsAccessKey.strip(), awsSecretKey.strip())
	
		try:
			buckets = connection.get_all_buckets()
		except:
			self.log('Invalid login credentials, please try again...')
			return
	
		self.config.set('aws-access-key', awsAccessKey)
		self.config.write()
	
		setpassword('aws', awsAccessKey, awsSecretKey)
	
		awsBucketName = self.config.get('aws-bucket-name') or raw_input('S3 bucket name: ').strip().lower()
	
		if awsBucketName not in [b.name for b in buckets]:
			if raw_input('Bucket does not exist, create it? (y/n): ') == 'y':
				
				try:
					awsBucket = connection.create_bucket(awsBucketName, policy='public-read')
				except boto.exception.S3CreateError, e:
					self.log('Bucket with name %s already is used by someone else, please try again with another name' % awsBucketName)
					return
					
				awsBucket.configure_website('index.html', 'error.html')
				
				self.config.set('aws-bucket-website', awsBucket.get_website_endpoint())
				self.config.set('aws-bucket-name', awsBucketName)
				self.config.write()
			
				self.log('Bucket %s was created with website endpoint %s' % (self.config.get('aws-bucket-name'), self.config.get('aws-bucket-website')))
				self.log('You can learn more about s3 (like pointing to your own domain) here: https://github.com/koenbok/Cactus')
			
			else: return
		else:
			for b in buckets:
				if b.name == awsBucketName:
					awsBucket = b
	
		self.log('Uploading site to bucket %s' % awsBucketName)
		
		self.changedFilesAtLastDeploy = []
		
		self.awsBucket = awsBucket
		filesToUpload = fileList(self.paths['build'])
		self.map(self.uploadFile, filesToUpload)
		
		self.execHook('postDeploy')
	
		self.log('')
		self.log('Upload done, %s of %s files changed' % (len(self.changedFilesAtLastDeploy), len(filesToUpload)))
		self.log('http://%s' % self.config.get('aws-bucket-website'))
		self.log('')
		
		# Expire cloudfront files
		if not self.changedFilesAtLastDeploy:
			return
		
		from boto import cloudfront
		
		connection = cloudfront.CloudFrontConnection(awsAccessKey.strip(), awsSecretKey.strip())
		
		if not self.config.get('aws-bucket-website'):
			return
		
		for d in connection.get_all_distributions():
			if d.origin.dns_name == self.config.get('aws-bucket-website').replace('http://', '') and d.status == 'Deployed':
				self.log('Sending CloudFront invalidation request to %s (cname: %s)' % (d.domain_name, ' '.join(d.cnames)))
				connection.create_invalidation_request(d.id, self.changedFilesAtLastDeploy)
				self.log('Request sent, can take up to fifteen minutes to process...')
				

def main(argv=sys.argv):
		
	def exit():
		print
		print 'Usage: cactus.py <path> [create|build|serve|deploy]'
		print 
		print '    create:  Create a new website skeleton at path'
		print '    build:   Rebuild your site from source files'
		print '    serve:   Serve you website at local development server'
		print '    deploy:  Upload and deploy your site to S3'
		print
		sys.exit()
	
	if len(argv) < 3:
		exit()

	# Handy shortcut for editing in TextMate
	if argv[2] == 'mate':
		commands.getstatusoutput('mate %s' % argv[1])
		return
	
	if argv[2] not in ['create', 'build', 'serve', 'deploy']:
		exit()
	
	path = os.path.abspath(sys.argv[1])
	
	if argv[2] != 'create':
		for p in ['pages', 'static', 'templates']:
			if not os.path.isdir(os.path.join(path, p)):
				print 'This does not look like a cactus project (missing "%s" subfolder)' % p
				sys.exit()
	
	getattr(Site(path), argv[2])()


###############################################################
### TEMPLATES

templateFile = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>Welcome</title>
	
	<link rel="shortcut icon" href="{{ STATIC_URL }}/favicon.ico"> 
	
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

errorFile = """{% extends "base.html" %}
{% block content %}
<script type="text/javascript" charset="utf-8" src="https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js"></script>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function() {
		
		// Add the missing url to the text
		$("#url").text(window.location.pathname);
		
		// Fix the css locations dynamically
		$("head link").each(function() {
			for (var i=0; i<window.location.pathname.split(/\//g).length-2; i++)
				$(this).attr("href", "../" + $(this).attr("href"));
		});
		
	})
</script>

<p>
	Sorry the page <b id="url"></b> could not be found on this server.
</p>
{% endblock %}
"""

robotsFile = """{% for path in CACTUS.pages %}{{ path }}
{% endfor %}"""

sitemapFile = """<?xml version="1.0" encoding="UTF-8"?> 
<urlset xmlns="http://www.google.com/schemas/sitemap/0.84"> 
{% for path in CACTUS.pages %}
	<url>
		<loc>{{ path }}</loc>
		<changefreq>daily</changefreq> 
		<priority>1.0</priority> 
	</url>
{% endfor %}
</urlset>
"""

renderFile = """def process(path, data):
	context = {}
	return context, data
"""

hooksFile = """import os

def preBuild(path, config):
	pass

def postBuild(path, config):
	pass

def preDeploy(path, config):
	
	# Add a deploy log at /versions.txt
	
	import urllib2
	import datetime
	import platform
	import codecs
	import getpass
	
	url = config.get('aws-bucket-website')
	data = u''
	
	try:
		data = urllib2.urlopen('http://%s/versions.txt' % url).read() + u'\\n'
	except:
		pass
	
	data += u'\t'.join([datetime.datetime.now().isoformat(), platform.node(), getpass.getuser()])
	codecs.open(os.path.join(path, 'build', 'versions.txt'), 'w', 'utf8').write(data)

def postDeploy(path, config):
	pass
"""

###############################################################
### MAIN

if __name__ == "__main__":
	main()
