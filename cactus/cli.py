#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import time
import argparse
import socket

from six.moves import input
import colorama

# No cactus imports here! There's no logging in place (or anything really).
# It's best to wait until we've ran setup_logging before running imports (some import soft errors log).


class CactusCli(object):
    """
    We wrap all imports into this object to control their order
    """
    def __init__(self):
        self.Site = None
        self.bootstrap = None

    def do_imports(self):
        from cactus.site import Site
        from cactus.bootstrap import bootstrap
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
            if input('Path %s exists, move aside to %s? (y/n) ' % (path, new_path)) == 'y':
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


def parse_arguments(cli, args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description="Build and deploy static websites using Django templates.")

    subparsers = parser.add_subparsers(title='subcommands', description='Valid subcommands',
                                       help='Select a command to run.', dest='command')
    subparsers.required = True

    parser_create = subparsers.add_parser('create', help='Create a new project')
    parser_create.add_argument('path', help='The path where the new project should be created')
    parser_create.add_argument('-s', '--skeleton', help='An archive to use as skeleton to create the new project')
    parser_create.set_defaults(target=cli.create)

    parser_build = subparsers.add_parser('build', help='Build the current project.')
    parser_build.set_defaults(target=cli.build)

    parser_deploy = subparsers.add_parser('deploy', help='Deploy the current project to S3.')
    parser_deploy.set_defaults(target=cli.deploy)

    parser_serve = subparsers.add_parser('serve', help='Serve the current project.')
    parser_serve.set_defaults(target=cli.serve)
    parser_serve.add_argument('-p', '--port', default=8000, type=int, help='The port on which to serve the site.')
    parser_serve.add_argument('-b', '--browser', action='store_true', help='Whether to open a browser for the site.')

    parser_make_messages = subparsers.add_parser('messages:make', help='Create translation files for the current project')
    parser_make_messages.set_defaults(target=cli.make_messages)

    parser_domain_setup = subparsers.add_parser('domain:setup', help='Setup records for a domain with route 53')
    parser_domain_setup.set_defaults(target=cli.domain_setup)

    parser_domain_list = subparsers.add_parser('domain:list', help='Setup records for a domain with route 53')
    parser_domain_list.set_defaults(target=cli.domain_list)


    config_parsers = [parser_build, parser_deploy, parser_serve, parser_make_messages, parser_domain_setup, parser_domain_list]
    all_parsers = config_parsers + [parser_create]

    for subparser in config_parsers:
        subparser.add_argument('-c', '--config', action="append",
                               help='Add a config file you want to use')
        subparser.add_argument('-d', '--path', default=os.getcwd(),
                               help='The path to the Cactus project')

    for subparser in all_parsers:
        verbosity_group = subparser.add_mutually_exclusive_group()
        verbosity_group.add_argument('-v', '--verbose', action='store_true', help='Be more verbose')
        verbosity_group.add_argument('-q', '--quiet', action='store_true', help='Be quieter')

    ns = parser.parse_args(args)

    # Small hack to provide a default value while not replacing what's
    # given by the user, if there is
    if hasattr(ns, 'config') and ns.config is None:  # We don't need config for create
        ns.config = [os.path.join(ns.path, 'config.json')]

    return ns

def main(args):
    cli = CactusCli()

    # CLI parsing
    ns = parse_arguments(cli, args)

    # Colors!
    colorama.init()

    # Logging
    from cactus.logger import setup_logging
    setup_logging(ns.verbose, ns.quiet)

    # Network setup that we should presumably remove. Leaving it there for now:
    # it's a better place than cactus/__init__.py
    socket.setdefaulttimeout(5)

    # Import Cactus packages and run required command.
    cli.do_imports()

    kwargs = dict((k, v) for k, v in vars(ns).items() if k not in ['command', 'target', 'verbose', 'quiet'])
    ns.target(**kwargs)


def cli_entrypoint():
    main(sys.argv[1:])


if __name__ == "__main__":
    cli_entrypoint()
