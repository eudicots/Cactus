#coding:utf-8
import logging

from cactus.bootstrap.archive import bootstrap_from_archive
from cactus.bootstrap.package import bootstrap_from_package


logger = logging.getLogger(__name__)


def bootstrap(path, skeleton=None):
    """
    Bootstrap a new project at a given path.

    :param path: The location where the new project should be created.
    :param skeleton: An optional path to an archive that should be used instead of the standard cactus skeleton.
    """

    if skeleton is None:
        bootstrap_from_package(path)
    else:
        bootstrap_from_archive(path, skeleton)

    logger.info('New project generated at %s', path)
