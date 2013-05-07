import os
import sys
import pipes
import shutil
import subprocess

from cactus.utils import fileList

"""
This plugin uses pyScss to translate sass files to css

Install:

sudo easy_install pyScss

"""

try:
	from scss import Scss
except:
	sys.exit("Could not find pyScss, please install: sudo easy_install pyScss")


CSS_PATH = 'static/css'

for path in fileList(CSS_PATH):
	
	if not path.endswith('.scss'):
		continue
	
	with open(path, 'r') as f:
		data = f.read()
	
	css = Scss().compile(data)

	with open(path.replace('.scss', '.css'), 'w') as f:
		f.write(css)