import posixpath
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
