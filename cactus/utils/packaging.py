import logging
import posixpath
import os
import pkg_resources


def pkg_walk(package, top):
    """
    Walk the package resources. Implementation from os.walk.
    """

    names = pkg_resources.resource_listdir(package, top)

    dirs, nondirs = [], []

    for name in names:
        # Forward slashes with pkg_resources
        if pkg_resources.resource_isdir(package, posixpath.join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    yield top, dirs, nondirs

    for name in dirs:
        new_path = posixpath.join(top, name)
        for out in pkg_walk(package, new_path):
            yield out


def bootstrap(path):
    """
    Bootstrap a new project at a given path.
    """

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
            with open(file_path, 'w') as f:
                f.write(pkg_resources.resource_stream("cactus", resource_path).read())

    logging.info('New project generated at %s', path)