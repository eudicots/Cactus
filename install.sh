#!/bin/sh

echo "Installing Cactus, hold on..."

cd /tmp

# Install setuptools

sudo python -c "import urllib; urllib.main()" http://peak.telecommunity.com/dist/ez_setup.py | python - -U setuptools

# Install dependencies

sudo easy_install baker
sudo easy_install django
sudo easy_install simplejson
sudo easy_install boto

# Install Cactus

curl -O https://github.com/koenbok/Cactus/raw/master/cactus.py
chmod 755 cactus.py
sudo mv cactus.py /usr/local/bin/cactus

echo
echo "If there were no errors, the installation of Cactus was successful"
echo "For more info see https://github.com/koenbok/Cactus"
echo