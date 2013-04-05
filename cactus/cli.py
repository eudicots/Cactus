#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import time
import cactus
import argparse

from cactus.utils import bootstrap


def create(path):
	"Creates a new project at the given path."
	
	if os.path.exists(path):
		if raw_input('Path %s exists, move aside (y/n): ' % path) == 'y':
			os.rename(path, '%s.%s.moved' % (path, int(time.time())))
		else:
			sys.exit()
	
	bootstrap(path)


def build(path, config, optimize):
	"Build a cactus project"
	
	site = cactus.Site(path, config, optimize = optimize)
	site.build()


def deploy(path, config, optimize):
	"Upload the project to S3"
	site = cactus.Site(path, config, optimize)
	site.upload()


def serve(path, config, optimize, port, browser):
	"Serve the project and watch changes"
	
	site = cactus.Site(path, config)
	site.serve(port=port, browser=browser)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Build and deploy static websites using Django templates.")

	subparsers = parser.add_subparsers(title = 'subcommands', description = 'Valid subcommands', help = 'Select a command to run.')

	parser_create = subparsers.add_parser('create', help = 'Create a new project')
	parser_create.add_argument('path', help = 'The path where the new project should be created')
	parser_create.set_defaults(target = create)

	parser_build = subparsers.add_parser('build', help = 'Build the current project.')
	parser_build.set_defaults(target = build)

	parser_serve = subparsers.add_parser('serve', help = 'Serve the current project.')
	parser_serve.set_defaults(target = serve)
	parser_serve.add_argument('-p', '--port', default = 8000, type = int, help = 'The port on which to serve the site.')
	parser_serve.add_argument('-b', '--browser', action = 'store_true', help = 'Whether to open a browser for the site.')

	parser_deploy = subparsers.add_parser('deploy', help = 'Deploy the current project to S3.')
	parser_deploy.set_defaults(target = deploy)

	for subparser in (parser_build, parser_serve, parser_deploy):
		subparser.add_argument('-o', '--optimize', action = 'store_true', help = 'Run optimizations on files.')
		subparser.add_argument('-c', '--config', default = 'config.json', help = 'Path to the config file you want to use.')
		subparser.set_defaults(path = os.getcwd())

	args = parser.parse_args()
	args.target(**{k:v for k, v in vars(args).items() if k != 'target'})
