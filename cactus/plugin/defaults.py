#coding:utf-8

# Define no-op plugin methods
def preBuildPage(page, context, data):
    return context, data


def postBuildPage(page):
    pass


def preBuildStatic(static):
    pass


def postBuildStatic(static):
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
    'preBuildStatic',
    'postBuildStatic',
    'preBuild',
    'postBuild',
    'preDeploy',
    'postDeploy',
    'preDeployFile',
]