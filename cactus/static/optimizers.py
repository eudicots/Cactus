#coding:utf-8
import subprocess
from cactus.static.external import ExternalProcessor


class ClosureJSOptimizer(ExternalProcessor):
    supported_extensions = ('js',)
    output_extension = 'js'

    def _run(self):
        subprocess.call([
            'closure-compiler',
            '--js', self.src,
            '--js_output_file', self.dst,
            '--compilation_level', 'SIMPLE_OPTIMIZATIONS'
        ])


class YUIJSOptimizer(ExternalProcessor):
    supported_extensions = ('js',)
    output_extension = 'js'

    def _run(self):
        subprocess.call([
            'yuicompressor',
            '--type', 'js',
            '-o', self.dst,
            self.src,
        ])


class YUICSSOptimizer(ExternalProcessor):
    supported_extensions = ('css',)
    output_extension = 'css'

    def _run(self):
        subprocess.call([
            'yuicompressor',
            '--type', 'css',
            '-o', self.dst,
            self.src,
        ])


optimizers = [ClosureJSOptimizer, YUIJSOptimizer, YUICSSOptimizer]