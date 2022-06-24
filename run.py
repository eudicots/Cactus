#!/usr/bin/env python
# encoding: utf-8
import sys
import cactus

from cactus.cli import main

print("Using: %s" % cactus.__file__)

if __name__ == "__main__":
    main(sys.argv[1:])
