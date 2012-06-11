import os

INFO = {
	'name': 'Version Updater',
	'description': 'Add a version to /versions.txt after eacht deploy'
}

# Set up extra django template tags

def templateTags():
	pass


# Build page actions

def preBuild(path, config, context, data):
	return context, data

def postBuild(path, config):
	pass


# Deploy actions

def preDeploy(path, config):
	
	# Add a deploy log at /versions.txt
	
	import urllib2
	import datetime
	import platform
	import codecs
	import getpass
	
	url = config.get('aws-bucket-website')
	data = u''
	
	# Get the current content of versions.txt
	try: data = urllib2.urlopen('http://%s/versions.txt' % url).read() + u'\n'
	except: pass
	
	data += u'\t'.join([datetime.datetime.now().isoformat(), platform.node(), getpass.getuser()])
	codecs.open(os.path.join(path, 'build', 'versions.txt'), 'w', 'utf8').write(data)

def postDeploy(path, config):
	pass
