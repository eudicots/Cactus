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


def init(path):
	"""
	New site skeleton.
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

def build(path):
	
	# Set up django
	
	templatePath = os.path.join(path, 'templates')
	contentsPath = os.path.join(path, 'contents')
	
	mediaPath = os.path.join(path, 'static')
	buildPath = os.path.join(path, 'build')
	
	from django.conf import settings
	settings.configure(TEMPLATE_DIRS=[templatePath, contentsPath])
	
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
	shutil.copytree(mediaPath, os.path.join(buildPath, 'static'))
	

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



# import shutil
# 
# shutil.rmtree('/Users/koen/testsite')
# init('/Users/koen/testsite')
build('/Users/koen/testsite')