#coding:utf-8
import subprocess

from cactus.static.external import External


class SASSProcessor(External):
    supported_extensions = ('sass',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call(['sass', self.src, self.dst])


class SCSSProcessor(External):
    supported_extensions = ('scss',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call(['sass', '--scss', self.src, self.dst])