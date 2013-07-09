# based on the example code from google
# would be better if the scripts were concatenated first, but that would involve
# another plugin and then would have to allow either explicit or implicit ordering
# of the files and then you'd have to setup an ordering of plugins to run...
import subprocess
from glob import glob

def postBuild(site):
    for script in glob('%s/static/js/*js' % site.paths['build']):
        root_name = script.rsplit(',', 1)[0]
        dest = "%s.min.js" % root_name
        try:
            subprocess.check_call(['java', '-jar', '/usr/local/lib/closure.jar', '--js', script, '--js_output_file', dest])
        except subprocess.CalledProcessError:
            print 'JS Compile step failed.'