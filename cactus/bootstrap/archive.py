#coding:utf-8
import os
import shutil
import tarfile
import zipfile

from six.moves import urllib


class Folder(object):
    def __init__(self, from_path):
        self.from_path = from_path

    def extractall(self, path):
        os.rmdir(path)
        shutil.copytree(self.from_path, path)

    def close(self):
        pass


def open_zipfile(archive):
    return zipfile.ZipFile(archive)


def open_tarfile(archive):
    return tarfile.open(name=archive, mode='r')


SUPPORTED_ARCHIVES = [
    (open_tarfile, tarfile.is_tarfile),
    (open_zipfile, zipfile.is_zipfile),
    (Folder, os.path.isdir),
]


def bootstrap_from_archive(path, skeleton):
    if os.path.isfile(skeleton) or os.path.isdir(skeleton):
        # Is is a local file?
        skeleton_file = skeleton
    else:
        # Assume it's an URL
        skeleton_file, headers = urllib.request.urlretrieve(skeleton)

    for opener, test in SUPPORTED_ARCHIVES:
        try:
            if test(skeleton_file):
                archive = opener(skeleton_file)
                break
        except IOError:
            pass
    else:
        raise Exception("Unsupported skeleton file type. Only .tar and .zip are supported at this time.")

    os.mkdir(path)
    archive.extractall(path=path)
    archive.close()
