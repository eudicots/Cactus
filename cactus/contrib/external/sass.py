#coding:utf-8
import subprocess
import platform

from cactus.static.external import External


_platform = platform.system()

if _platform in ("Darwin", "Linux"):
    SASS_PATH = "sass"
elif _platform in ("Windows",):
    SASS_PATH = "sass.bat"
else:
    #TODO: Java?
    pass


#TODO: Extra args to make "nice to read" output (the optimizer will fix it)
class SASSProcessor(External):
    supported_extensions = ('sass',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call([SASS_PATH, self.src, self.dst])


class SCSSProcessor(External):
    supported_extensions = ('scss',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call([SASS_PATH, '--scss', self.src, self.dst])