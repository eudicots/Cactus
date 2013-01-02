import os
import sys
import subprocess
import shutil

from setuptools import setup
from distutils.sysconfig import get_python_lib

VERSION = "2.1.3"

if "uninstall" in sys.argv:
	
	def run(command):
		try:
			return subprocess.check_output(command, shell=True).strip()
		except subprocess.CalledProcessError:
			pass
	

	cactusBinPath = run('which cactus')
	cactusPackagePath = None
	
	for p in os.listdir(get_python_lib()):
		if p.lower().startswith('cactus') and p.lower().endswith('.egg'):
			cactusPackagePath = os.path.join(get_python_lib(), p)

	if cactusBinPath and os.path.exists(cactusBinPath):
		print 'Removing cactus script at %s' % cactusBinPath
		os.unlink(cactusBinPath)
	
	if cactusPackagePath and os.path.isdir(cactusPackagePath):
		print 'Removing cactus package at %s' % cactusPackagePath
		shutil.rmtree(cactusPackagePath)

	sys.exit()

if "install" in sys.argv or "bdist_egg" in sys.argv:
	
	# Check if we have an old version of cactus installed
	p1 = '/usr/local/bin/cactus.py'
	p2 = '/usr/local/bin/cactus.pyc'
	
	if os.path.exists(p1) or os.path.exists(p2):
		print "Error: you have an old version of Cactus installed, we need to move it:"
		if os.path.exists(p1): print "  sudo rm %s" % p1 
		if os.path.exists(p2): print "  sudo rm %s" % p2
		sys.exit()

setup(
	name='Cactus',
	version=VERSION,
	description="Static site generation and deployment.",
	long_description=open('readme.md').read(),
	url='http://github.com/koenbok/Cactus',
	download_url='https://github.com/koenbok/Cactus/tarball/v%s#egg=Cactus-%s' % (VERSION, VERSION),
	author='Koen Bok',
	author_email='koen@madebysofa.com',
	license='BSD',
	packages=['cactus'],
	entry_points={
		'console_scripts': [
			'cactus = cactus.cli:main',
		],
	},
	install_requires=[
		'Django',
		'boto>=2.4.1',
		'markdown',
		'PyYAML',
	],
	zip_safe=False,
	tests_require=['nose'],
	test_suite='nose.collector',
	classifiers=[],
)
