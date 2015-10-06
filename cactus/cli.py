#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import time
import argparse
import socket

import colorama

# No cactus imports here! There's no logging in place (or anything really).
# It's best to wait until we've ran setup_logging before running imports (some import soft errors log).


class CactusCli(object):
    """
    We wrap all imports into this object to control their order
    """
    def __init__(self, Site, bootstrap):

        self.Site = Site
        self.bootstrap = bootstrap


    def create(self, path, skeleton=None):
        """
        Creates a new project at the given path.

        :param path: The path where the new project should be created
        :param skeleton: An (optional) skeleton to use to create the project.
                         This could be a zip, tar archive (file path or URL)
        """

        if os.path.exists(path):
            new_path = '%s.%s.moved' % (path, int(time.time()))
            if raw_input('Path %s exists, move aside to %s? (y/n) ' % (path, new_path)) == 'y':
                os.rename(path, new_path)
            else:
                sys.exit()

        self.bootstrap(path, skeleton)


    def build(self, path, config):
        """Build a cactus project"""

        site = self.Site(path, config)
        site.build()


    def deploy(self, path, config):
        """Upload the project to S3"""
        site = self.Site(path, config)
        site.upload()


    def make_messages(self, path, config):
        """ Create the list of translation files for the site """
        site = self.Site(path, config)
        site.make_messages()


    def serve(self, path, config, port, browser):
        """Serve the project and watch changes"""
        site = self.Site(path, config)
        site.serve(port=port, browser=browser)

    def domain_setup(self, path, config):
        site = self.Site(path, config)
        site.domain_setup()

    def domain_list(self, path, config):
        site = self.Site(path, config)
        site.domain_list()


def main():
    # Basic UI and logging setup
    colorama.init()

    from cactus.logger import setup_logging
    setup_logging()

    # Network setup that we should presumably remove. Leaving it there for now:
    # it's a better place than cactus/__init__.py

    socket.setdefaulttimeout(5)

    # Cactus imports

    from cactus.site import Site
    from cactus.bootstrap import bootstrap

    cli = CactusCli(Site, bootstrap)

    # Actual CLI parsing

    parser = argparse.ArgumentParser(description = "Build and deploy static websites using Django templates.")

    subparsers = parser.add_subparsers(title = 'subcommands', description = 'Valid subcommands',
                                       help = 'Select a command to run.')

    parser_create = subparsers.add_parser('create', help='Create a new project')
    parser_create.add_argument('path', help='The path where the new project should be created')
    parser_create.add_argument('-s', '--skeleton', help='An archive to use as skeleton to create the new project')
    parser_create.set_defaults(target=cli.create)

    parser_build = subparsers.add_parser('build', help = 'Build the current project.')
    parser_build.set_defaults(target=cli.build)

    parser_deploy = subparsers.add_parser('deploy', help = 'Deploy the current project to S3.')
    parser_deploy.set_defaults(target=cli.deploy)

    parser_serve = subparsers.add_parser('serve', help = 'Serve the current project.')
    parser_serve.set_defaults(target=cli.serve)
    parser_serve.add_argument('-p', '--port', default = 8000, type = int, help = 'The port on which to serve the site.')
    parser_serve.add_argument('-b', '--browser', action = 'store_true',
                              help = 'Whether to open a browser for the site.')

    parser_make_messages = subparsers.add_parser('messages:make', help='Create translation files for the current project')
    parser_make_messages.set_defaults(target=cli.make_messages)

    parser_domain_setup = subparsers.add_parser('domain:setup', help='Setup records for a domain with route 53')
    parser_domain_setup.set_defaults(target=cli.domain_setup)

    parser_domain_list = subparsers.add_parser('domain:list', help='Setup records for a domain with route 53')
    parser_domain_list.set_defaults(target=cli.domain_list)


    for subparser in (parser_build, parser_deploy, parser_serve, parser_make_messages, parser_domain_setup, parser_domain_list):
        subparser.add_argument('-c', '--config', action="append",
                               help='Add a config file you want to use')

        subparser.set_defaults(path = os.getcwd())

    args = parser.parse_args()

    # Small hack to provide a default value while not replacing what's
    # given by the user, if there is
    if hasattr(args, 'config') and args.config is None:  # We don't need config for create
        args.config = ["config.json"]

    args.target(**{k: v for k, v in vars(args).items() if k != 'target'})


if __name__ == "__main__":
    main()
