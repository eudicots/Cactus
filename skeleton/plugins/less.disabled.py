import subprocess
from glob import glob

def postBuild(site):
    for filename in glob('%s/static/css/*less' % site.paths['build']):
        root_name = filename.rsplit('.', 1)[0]
        src = filename
        dest = "%s.css" % root_name
        try:
            subprocess.check_call(['lessc', '--compress', src, dest])
        except subprocess.CalledProcessError:
            print "lessc returned a non-zero exit status, please check your less syntax"