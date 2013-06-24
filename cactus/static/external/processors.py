#coding:utf-8
import subprocess

from cactus.static.external import paths, External


class SASSProcessor(External):
    supported_extensions = ('sass',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call([paths.SASS_PATH, self.src, self.dst])


#TODO: Extra args to make "nice to read" output (the optimize will fix it)
class SCSSProcessor(External):
    supported_extensions = ('scss',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call([paths.SASS_PATH, '--scss', self.src, self.dst])