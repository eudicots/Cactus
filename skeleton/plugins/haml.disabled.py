import sys
import os
import codecs

from cactus.utils import fileList
from hamlpy.hamlpy import Compiler



CLEANUP = []

def preBuild(site):
    for path in fileList(site.paths['pages']):
        

        if not path.endswith('.haml'):
            continue


        
        haml_lines = codecs.open(path, 'r', encoding='utf-8').read().splitlines()
 
        compiler = Compiler()
        output = compiler.process_lines(haml_lines)
        outPath = path.replace('.haml', '.html')

        print outPath
        with open(outPath,'w') as f:
            f.write(output)

        CLEANUP.append(outPath)


def postBuild(site):
    global CLEANUP
    for path in CLEANUP:
        print path
        os.remove(path)
    CLEANUP = []