#!/bin/sh

echo "Installing Cactus, hold on..."

cd /tmp

# Install setuptools

python -c "import urllib; urllib.main()" http://peak.telecommunity.com/dist/ez_setup.py | sudo python - -U setuptools

# Install dependencies

sudo easy_install django
sudo easy_install simplejson
sudo easy_install workerpool
# sudo easy_install boto

# Install boto from github as we need the latest version

curl -L https://github.com/boto/boto/tarball/master > boto.tar.gz
tar -zxvf boto.tar.gz
mv boto-boto* boto
cd boto
sudo python setup.py install

# Install Cactus

curl -O https://github.com/koenbok/Cactus/raw/master/cactus.py
chmod 755 cactus.py
sudo mv cactus.py /usr/local/bin/cactus.py

echo
echo "If there were no errors, the installation of Cactus was successful"
echo "For more info see https://github.com/koenbok/Cactus"
echo