#!/usr/bin/env python
# encoding: utf-8
"""
cactus.py

Created by Koen Bok on 2011-02-26.
Copyright (c) 2011 Sofa BV. All rights reserved.
"""

import sys
import os
import codecs
import shutil
import baker

from distutils import dir_util

from django.template import Template, Context
from django.template import loader as templateLoader


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


@baker.command
def init(path):
	"""
	Generate new site at path
	"""
	
	os.mkdir(path)
	
	# Generate basic structure
	for d in ['templates', 'static', 'static/css', 'static/js', 'static/images', 'contents', 'build']:
		os.mkdir(os.path.join(path, d))
	
	# Generate some default files
	open(os.path.join(path, 'templates', 'base.html'), 'w').write(templateFile)
	open(os.path.join(path, 'contents', 'index.html'), 'w').write(indexFile)
	open(os.path.join(path, 'contexts.py'), 'w').write(contextsFile)
	open(os.path.join(path, 'templatetags.py'), 'w').write("")

@baker.command
def build(path):
	"""
	Rebuild site at path
	"""
	# Set up django
	
	templatePath = os.path.join(path, 'templates')
	contentsPath = os.path.join(path, 'contents')
	
	staticPath = os.path.join(path, 'static')
	buildPath = os.path.join(path, 'build')
	
	try:
		from django.conf import settings
		settings.configure(TEMPLATE_DIRS=[templatePath, contentsPath])
	except:
		pass
	
	sys.path.append(path)
	import contexts
	import templatetags

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
	
	map(buildPage, [f.replace('%s/' % contentsPath, '') for f in fileList(contentsPath)])
	
	dir_util.copy_tree(staticPath, os.path.join(buildPath, 'static'), verbose=1)

@baker.command
def listen(path):
	
	buildPath = os.path.join(path, 'build')
	
	from pyfsevents import registerpath, listen
	
	def rebuild(change, recursive):
		if not change.startswith(buildPath):
			build(path)
	
	registerpath(path, rebuild)
	listen()

@baker.command
def serve(path, port=8000):
	
	buildPath = os.path.join(path, 'build')
	
	import SimpleHTTPServer
	import SocketServer
	
	os.chdir(buildPath)
	
	httpd = SocketServer.TCPServer(("", port), SimpleHTTPServer.SimpleHTTPRequestHandler)
	print "serving at port", port
	httpd.serve_forever()

### TEMPLATES

templateFile = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
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

indexFile = """
{% extends "base.html" %}
{% block content %}
Hello world!
{% endblock %}
"""

contextsFile = """
def context(url):
	return {}
"""

baker.run()
