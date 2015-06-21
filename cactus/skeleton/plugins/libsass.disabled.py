import sys
from cactus.utils.filesystem import fileList
try:
    import sass
except:
    sys.exit("Could not find libsass, please install: sudo easy_install libsass")

CSS_PATH = 'static/css'

def postBuild(site):
    for path in fileList(CSS_PATH):
        if not path.endswith('.scss'):
            continue

        with open(path, 'rw') as f:
            data = f.read()

        css, map = sass.compile(filename=path,
                                source_map_filename=path.replace('.scss', '.css') + ".map",
        )
        with open(path.replace('.scss', '.css'), 'w') as f:
            f.write(css)
        with open(path.replace('.scss', '.css') + ".map", "wb") as mapsock:
            mapsock.write(map.encode('utf8'))
