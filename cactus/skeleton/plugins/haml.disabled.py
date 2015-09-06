import sys
import os
import codecs

# How to:
#     * Install hamlpy (https://github.com/jessemiller/HamlPy)
#     * .haml files will compiled to .html files


from hamlpy.hamlpy import Compiler
from cactus.utils.filesystem import fileList

CLEANUP = []

def preBuild(site):
    for path in fileList(site.paths['pages']):

        #only file ends with haml
        if not path.endswith('.haml'):
            continue

        #read the lines
        haml_lines = codecs.open(path, 'r', encoding='utf-8').read().splitlines()

        #compile haml to html
        compiler = Compiler()
        output = compiler.process_lines(haml_lines)

        #replace path
        outPath = path.replace('.haml', '.html')

        #write the html file
        with open(outPath,'w') as f:
            f.write(output)

        CLEANUP.append(outPath)


def postBuild(site):
    global CLEANUP
    for path in CLEANUP:
        print path
        os.remove(path)
    CLEANUP = []
