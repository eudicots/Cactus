#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import time

import cactus

import argparse

description = '''
Usage: cactus [create|build|serve|deploy]

    create: Create a new website skeleton at path
    build: Rebuild your site from source files
    serve <port>: Serve you website at local development server
    deploy: Upload and deploy your site to S3

'''
def _init_parser():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('command', metavar='COMMAND', help='The command to execute (one of [create|build|serve|deploy] )')
    parser.add_argument('option1', metavar='OPTION1', nargs='?', help='option 1')
    parser.add_argument('option2', metavar='OPTION2', nargs='?', help='option 2')
    parser.add_argument('--skeleton', required=False, help="If provided, the path to a .tar.gz file or a directory which will be used in place of the default 'skeleton' for a cactus project.")
    return parser

def create(path, args):
	"Creates a new project at the given path."
	
	if os.path.exists(path):
		if raw_input('Path %s exists, move aside (y/n): ' % path) == 'y':
			os.rename(path, '%s.%s.moved' % (path, int(time.time())))
		else:
			sys.exit()
	
	site = cactus.Site(path)
	site.bootstrap(skeleton=args.skeleton)


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
	print description

def exit(msg):
	print msg
	sys.exit()

def main():
	
	parser = _init_parser()
	args = parser.parse_args()
	command = args.command
	option1 = args.option1
	option2 = args.option2
	
	# If we miss a command we exit and print help
	if not command:
		help()
		sys.exit()
	
	# Run the command
	if command == 'create':
		if not option1: exit('Missing path')
		create(option1, args)
	
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