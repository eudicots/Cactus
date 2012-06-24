import os
import pipes

def postBuild(site):
	os.system('coffee -c %s/static/js/*.coffee' % pipes.quote(site.paths['build']))