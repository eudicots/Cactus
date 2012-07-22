import os
import sys
import pipes
import shutil
import subprocess

"""
This plugin uses glue to sprite images:
http://glue.readthedocs.org/en/latest/quickstart.html

Install:

(Only if you want to sprite jpg too)
brew install libjpeg

(Only if you want to optimize pngs with optipng)
brew install optipng

sudo easy_install pip
sudo pip uninstall pil
sudo pip install pil
sudo pip install glue
"""

try:
	import glue
except Exception, e:
	sys.exit('Could not use glue: %s\nMaybe install: sudo easy_install glue' % e)


IMG_PATH = 'static/img/sprites'
CSS_PATH = 'static/css/sprites'

KEY = '_PREV_CHECKSUM'

def checksum(path):
	command = 'md5 `find %s -type f`' % pipes.quote(IMG_PATH)
	return subprocess.check_output(command, shell=True)

def preBuild(site):
	
	currChecksum = checksum(IMG_PATH)
	prevChecksum = getattr(site, KEY, None)
	
	# Don't run if none of the images has changed
	if currChecksum == prevChecksum:
		return
	
	if os.path.isdir(CSS_PATH):
		shutil.rmtree(CSS_PATH)
	
	os.mkdir(CSS_PATH)
	os.system('glue --cachebuster --crop --optipng "%s" "%s" --project' % (IMG_PATH, CSS_PATH))
	
	setattr(site, KEY, currChecksum)