# based on the example code from google
# would be better if the scripts were concatenated first, but that would involve
# another plugin and then would have to allow either explicit or implicit ordering
# of the files and then you'd have to setup an ordering of plugins to run...
import httplib
import urllib
import sys
from glob import glob

def postBuild(site):
    for script in glob('%s/static/js/*js' % site.paths['build']):
        options = urllib.urlencode([
            ('js_code', script),
            ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),
            ('output_format', 'text'),
            ('output_info', 'compiled_code'),])

        root_name = script.rsplit(',', 1)[0]
        dest = "%s.min.js" % root_name

        headers = { "Content-type": "application/x-www-form-urlencoded" }
        conn = httplib.HTTPConnection('closure-compiler.appspot.com')
        conn.request('POST', '/compile', options, headers)
        response = conn.getresponse()
        data = response.read()
        with open(dest, 'w') as fh:
            fh.write(data);
        conn.close