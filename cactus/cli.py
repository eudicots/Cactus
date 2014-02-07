#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging
import time
import argparse

import cactus

from cactus.bootstrap import bootstrap
from cactus.logger import setup_logging

def create(path, skeleton=None):
    """
    Creates a new project at the given path.

    :param path: The path where the new project should be created
    :param skeleton: An (optional) skeleton to use to create the project.
                     This could be a zip, tar archive (file path or URL)
    """

    if os.path.exists(path):
        if raw_input('Path %s exists, move aside (y/n): ' % path) == 'y':
            os.rename(path, '%s.%s.moved' % (path, int(time.time())))
        else:
            sys.exit()

    bootstrap(path, skeleton)


def build(path, config):
    """Build a cactus project"""

    site = cactus.Site(path, config)
    site.build()


def deploy(path, config):
    """Upload the project to S3"""
    site = cactus.Site(path, config)
    site.upload()


def make_messages(path, config):
    """ Create the list of translation files for the site """
    site = cactus.Site(path, config)
    site.make_messages()


def serve(path, config, port, browser):
    """Serve the project and watch changes"""
    site = cactus.Site(path, config)
    site.serve(port=port, browser=browser)

def domain_setup(path, config):
    site = cactus.Site(path, config)
    site.domain_setup()

def domain_list(path, config):
    site = cactus.Site(path, config)
    site.domain_list()



def main():
    parser = argparse.ArgumentParser(description = "Build and deploy static websites using Django templates.")

    subparsers = parser.add_subparsers(title = 'subcommands', description = 'Valid subcommands',
                                       help = 'Select a command to run.')

    parser_create = subparsers.add_parser('create', help='Create a new project')
    parser_create.add_argument('path', help='The path where the new project should be created')
    parser_create.add_argument('-s', '--skeleton', help='An archive to use as skeleton to create the new project')
    parser_create.set_defaults(target=create)

    parser_build = subparsers.add_parser('build', help = 'Build the current project.')
    parser_build.set_defaults(target = build)

    parser_deploy = subparsers.add_parser('deploy', help = 'Deploy the current project to S3.')
    parser_deploy.set_defaults(target = deploy)

    parser_serve = subparsers.add_parser('serve', help = 'Serve the current project.')
    parser_serve.set_defaults(target = serve)
    parser_serve.add_argument('-p', '--port', default = 8000, type = int, help = 'The port on which to serve the site.')
    parser_serve.add_argument('-b', '--browser', action = 'store_true',
                              help = 'Whether to open a browser for the site.')

    parser_make_messages = subparsers.add_parser('messages:make', help='Create translation files for the current project')
    parser_make_messages.set_defaults(target=make_messages)

    parser_domain_setup = subparsers.add_parser('domain:setup', help='Setup records for a domain with route 53')
    parser_domain_setup.set_defaults(target=domain_setup)

    parser_domain_list = subparsers.add_parser('domain:list', help='Setup records for a domain with route 53')
    parser_domain_list.set_defaults(target=domain_list)


    for subparser in (parser_build, parser_deploy, parser_serve, parser_make_messages, parser_domain_setup, parser_domain_list):
        subparser.add_argument('-c', '--config', action="append",
                               help='Add a config file you want to use')

        subparser.set_defaults(path = os.getcwd())

    args = parser.parse_args()

    # Small hack to provide a default value while not replacing what's
    # given by the user, if there is
    if hasattr(args, 'config') and args.config is None:  # We don't need config for create
        args.config = ["config.json"]

    setup_logging()

    args.target(**{k: v for k, v in vars(args).items() if k != 'target'})


if __name__ == "__main__":
    main()
