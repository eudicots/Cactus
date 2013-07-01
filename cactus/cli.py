#!/usr/bin/env python
# encoding: utf-8
from optparse import OptionParser

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
    print 'Usage: cactus [create|build|serve|deploy|i18nlint]'
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
            try:
                option1 = int(option1)
            except:
                exit('port should be a round number like 5000, 8000, 8080')
        else:
            option1 = 8000

        browser = False if option2 == '-n' else True

        serve(os.getcwd(), port=option1, browser=browser)

    elif command == 'deploy':
        deploy(os.getcwd())

    elif command == 'i18nlint':
        parser = OptionParser(usage="usage: %prog [options]")
        parser.add_option("-r", "--replace", action="store_true", dest="replace",
                help="Ask to replace the strings in the file.", default=False)

        parser.add_option("-f", "--filename", action="store", dest="filename",
                help="Input one filename.", default=False)
        (options, args) = parser.parse_args()
        from i18nlint import replace_strings, print_strings

        def run_i18nlint(filename):
            if options.replace:
                replace_strings(filename)
            else:
                print_strings(filename)

        if options.filename:
            run_i18nlint(options.filename)
        else:
            for root, dirs, files in os.walk('pages'):
                for name in files:
                    if '.svn' not in root:
                        if 'html' in name and '_translated' not in name:
                            change = raw_input("Run i18nlint on file '%s/%s'? [Y/n] " % (root, name))
                            if change == 'y' or change == "":
                                run_i18nlint(os.path.join(root, name))

        if len(args) > 2:
            print "ERROR: Too many arguments"
            help()

    else:
        print 'Unknown command: %s' % command
        help()

if __name__ == "__main__":
    sys.exit(main())