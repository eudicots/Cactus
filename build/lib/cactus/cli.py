#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import time

import baker
import cactus

@baker.command(params={"path": "Path to create project at"})
def create(path):
	"Creates a new project at the given path."
	
	if os.path.exists(path):
		if raw_input('Path %s exists, move aside (y/n): ' % path) == 'y':
			os.rename(path, '%s.%s.moved' % (path, int(time.time())))
		else:
			sys.exit()
	
	site = cactus.Site(path)
	site.bootstrap()

@baker.command
def build(path=os.getcwd()):
	"Build a cactus project"
	
	site = cactus.Site(path)
	site.verify()
	site.build()

@baker.command
def serve(port=8000, path=os.getcwd()):
	"Serve the project and watch changes"
	
	site = cactus.Site(path)
	site.verify()
	site.serve(port=port)

@baker.command
def deploy(path=os.getcwd()):
	"Upload the project to S3"
	
	site = cactus.Site(path)
	site.verify()
	site.upload()

# @baker.command
# def help():
# 	print 'Usage: cactus [create|build|serve|deploy|update]'
# 	print 
# 	print '    create <path>: Create a new website skeleton at path'
# 	print '    build: Rebuild your site from source files'
# 	print '    serve: Serve you website at local development server'
# 	print '    deploy: Upload and deploy your site to S3'
# 	print ''
# 	print 'Or type "cactus.py update" to update to the latest version'
# 	print

def main(argv=None):
	try:
		baker.run()
	except baker.CommandError, e:
		print e
		print
		# baker.usage()