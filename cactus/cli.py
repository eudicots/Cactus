#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import time

import cactus

def create(path):
	"Creates a new project at the given path."
	
	if os.path.exists(path):
		if raw_input('Path %s exists, move aside (y/n): ' % path) == 'y':
			os.rename(path, '%s.%s.moved' % (path, int(time.time())))
		else:
			sys.exit()
	
	site = cactus.Site(path)
	site.bootstrap()


def build(path):
	"Build a cactus project"
	
	site = cactus.Site(path)
	site.verify()
	site.build()

def serve(path, port=8000, browser=True):
	"Serve the project and watch changes"
	
	site = cactus.Site(path)
	site.verify()
	site.serve(port=port, browser=browser)

def deploy(path):
	"Upload the project to S3"
	
	site = cactus.Site(path)
	site.verify()
	site.upload()

def help():
	print
	print 'Usage: cactus [create|build|serve|deploy]'
	print
	print '    create: Create a new website skeleton at path'
	print '    build: Rebuild your site from source files'
	print '    serve <port>: Serve you website at local development server'
	print '    deploy: Upload and deploy your site to S3'
	print

def exit(msg):
	print msg
	sys.exit()

def main():
	
	command = sys.argv[1] if len(sys.argv) > 1 else None
	option1 = sys.argv[2] if len(sys.argv) > 2 else None
	option2 = sys.argv[3] if len(sys.argv) > 3 else None
	
	# If we miss a command we exit and print help
	if not command:
		help()
		sys.exit()

	# Run the command
	if command == 'create':
		if not option1: exit('Missing path')
		create(option1)

	elif command == 'build':
		build(os.getcwd())

	elif command == 'serve':
		
		if option1:
			try: option1 = int(option1)
			except: exit('port should be a round number like 5000, 8000, 8080')
		else:
			option1 = 8000

		browser = False if option2 == '-n' else True

		serve(os.getcwd(), port=option1, browser=browser)

	elif command == 'deploy':
		deploy(os.getcwd())

	else:
		print 'Unknown command: %s' % command
		help()

if __name__ == "__main__":
	sys.exit(main())