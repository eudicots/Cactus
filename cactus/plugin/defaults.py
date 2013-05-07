#coding:utf-8

# Define no-op plugin methods
def preBuildPage(page, context, data):
    return context, data


def postBuildPage(page):
    pass


def preBuild(site):
    pass


def postBuild(site):
    pass


def preDeploy(site):
    pass


def postDeploy(site):
    pass


def preDeployFile(file):
    pass


ORDER = -1


DEFAULTS = [
    'preBuildPage',
    'postBuildPage',
    'preBuild',
    'postBuild',
    'preDeploy',
    'postDeploy',
    'preDeployFile',
]