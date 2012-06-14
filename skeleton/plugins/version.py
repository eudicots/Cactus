import os

INFO = {
	'name': 'Version Updater',
	'description': 'Add a version to /versions.txt after each deploy'
}

# Set up extra django template tags

def templateTags():
	pass


# Build actions

# def preBuild(site):
# 	print 'preBuild'
# 
# def postBuild(site):
# 	print 'postBuild'

# Build page actions

# def preBuildPage(site, path, context, data):
# 	print 'preBuildPage', path
# 	return context, data
# 
# def postBuildPage(site, path):
# 	print 'postBuildPage', path
# 	pass


# Deploy actions

def preDeploy(site):
	
	# Add a deploy log at /versions.txt
	
	import urllib2
	import datetime
	import platform
	import codecs
	import getpass
	
	url = site.config.get('aws-bucket-website')
	data = u''
	
	# Get the current content of versions.txt
	try: data = urllib2.urlopen('http://%s/versions.txt' % url).read() + u'\n'
	except: pass
	
	data += u'\t'.join([datetime.datetime.now().isoformat(), platform.node(), getpass.getuser()])
	codecs.open(os.path.join(site.paths['build'], 'versions.txt'), 'w', 'utf8').write(data)

def postDeploy(site):
	pass
