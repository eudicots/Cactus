#coding:utf-8
import subprocess

from cactus.static.external import ExternalProcessor


class SASSProcessor(ExternalProcessor):
    supported_extensions = ('sass',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call(['sass', self.src, self.dst])


class SCSSProcessor(ExternalProcessor):
    supported_extensions = ('scss',)
    output_extension = 'css'
    critical = True

    def _run(self):
        subprocess.call(['sass', '--scss', self.src, self.dst])


processors = [SASSProcessor, SCSSProcessor]