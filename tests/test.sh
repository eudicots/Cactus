#!/bin/sh

cactus create /tmp/catus-test

cd /tmp/catus-test

cactus build
cactus serve

rm -Rf /tmp/catus-test