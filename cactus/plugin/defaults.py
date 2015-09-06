#coding:utf-8

# Define no-op plugin methods
def preBuildPage(page, context, data):
    """
    Called prior to building a page.

    :param page: The page about to be built
    :param context: The context for this page (you can modify this, but you must return it)
    :param data: The raw body for this page (you can modify this).
    :returns: Modified (or not) context and data.
    """
    return context, data


def postBuildPage(page):
    """
    Called after building a page.

    :param page: The page that was just built.
    :returns: None
    """
    pass


def preBuildStatic(static):
    """
    Called before building (copying to the build folder) a static file.

    :param static: The static file about to be built.
    :returns: None
    """
    pass


def postBuildStatic(static):
    """
    Called after building (copying to the build folder) a static file.

    :param static: The static file that was just built.
    :returns: None
    """
    pass


def preBuild(site):
    """
    Called prior to building the site, after loading configuration and plugins.

    A good time to register your externals.

    :param site: The site about to be built.
    :returns: None
    """
    pass

def postBuild(site):
    """
    Called after building the site.

    :param site: The site that was just built.
    :returns: None
    """
    pass


def preDeploy(site):
    """
    Called prior to deploying the site (built files)

    A good time to configure custom headers

    :param site: The site about to be deployed.
    :returns: None
    """
    pass


def postDeploy(site):
    """
    Called after deploying the site (built files)

    :param site: The site that was just built.
    :returns: None
    """
    pass


def preDeployFile(file):
    """
    Called prior to deploying a single built file

    :param file: The file about to be deployed.
    :returns: None
    """
    pass


ORDER = -1


DEFAULTS = [
    'preBuildPage',
    'postBuildPage',
    'preBuildStatic',
    'postBuildStatic',
    'preBuild',
    'postBuild',
    'preDeploy',
    'postDeploy',
    'preDeployFile',
]
