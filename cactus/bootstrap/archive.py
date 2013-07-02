#coding:utf-8
import os
import urllib
import tarfile
import zipfile


def open_zipfile(archive):
    return zipfile.ZipFile(archive)

def open_tarfile(archive):
    return tarfile.open(name=archive, mode='r')


SUPPORTED_ARCHIVES = [
    (open_tarfile, tarfile.is_tarfile),
    (open_zipfile, zipfile.is_zipfile),
]


def bootstrap_from_archive(path, skeleton):
    if os.path.isfile(skeleton):
        # Is is a local file?
        skeleton_file = skeleton
    else:
        # Assume it's an URL
        skeleton_file, headers = urllib.urlretrieve(skeleton)

    for opener, test in SUPPORTED_ARCHIVES:
        if test(skeleton_file):
            archive = opener(skeleton_file)
            break
    else:
        raise Exception("Unsupported skeleton file type. Only .tar and .zip are supported at this time.")

    os.mkdir(path)
    archive.extractall(path=path)
    archive.close()