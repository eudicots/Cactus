#coding:utf-8
import os
import posixpath #TODO: Windows?
import logging
import pkg_resources

from cactus.utils.packaging import pkg_walk


def bootstrap_from_package(path):
    for dir_, sub_dirs, filenames in pkg_walk("cactus", "skeleton"):
        base_path = os.path.join(path, dir_.split('skeleton', 1)[1].lstrip('/'))

        for sub_dir in sub_dirs:
            dir_path = os.path.join(base_path, sub_dir)
            logging.debug("Creating {0}".format(dir_path))
            os.makedirs(dir_path)

        for filename in filenames:
            resource_path = posixpath.join(dir_, filename)
            file_path = os.path.join(base_path, filename)

            logging.debug("Copying {0} to {1}".format(resource_path, file_path))
            with open(file_path, 'wb') as f:
                f.write(pkg_resources.resource_stream("cactus", resource_path).read())