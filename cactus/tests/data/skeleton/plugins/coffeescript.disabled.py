import os
import pipes

os.environ['PATH'] = '/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/share/npm/bin:'

def postBuild(site):
	command = 'coffee -c %s/static/js/*.coffee' % pipes.quote(site.paths['build'])
	os.system(command)
