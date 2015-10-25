import os
import shutil
import tempfile
from contextlib import contextmanager

from cactus.utils.helpers import map_apply


def mkdtemp():
    return tempfile.mkdtemp(dir=os.environ.get("TEMPDIR"))

def fileList(paths, relative=False, folders=False):
    """
    Generate a recursive list of files from a given path.
    """

    if not isinstance(paths, list):
        paths = [paths]

    files = []

    def append(directory, name):
        if not name.startswith('.'):
            path = os.path.join(directory, name)
            files.append(path)

    for path in paths:
        for directory, dirnames, filenames in os.walk(path, followlinks=True):
            if folders:
                for dirname in dirnames:
                    append(directory, dirname)
            for filename in filenames:
                append(directory, filename)
        if relative:
            files = map_apply(lambda x: x[len(path) + 1:], files)

    return files


@contextmanager
def alt_file(current_file):
    """
    Create an alternate file next to an existing file.
    """
    _alt_file = current_file + '-alt'
    yield _alt_file
    try:
        shutil.move(_alt_file, current_file)
    except IOError:
        # We didn't use an alt file.
        pass


@contextmanager
def chdir(new_dir):
    """
    Chdir to another directory for an operation
    """
    current_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(current_dir)
