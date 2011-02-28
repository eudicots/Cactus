#!/bin/sh

echo "Installing Cactus, hold on..."

cd /tmp

# Install dependencies

easy_install baker django simplejson keyring boto pyfsevents

# Install Cactus

curl -O https://github.com/koenbok/Cactus/raw/master/cactus.py
chmod 755 cactus.py
mv cactus.py /usr/local/bin/cactus

echo
echo "If there were no errors, the installation of Cactus was successful"
echo "For more info see https://github.com/koenbok/Cactus"
echo