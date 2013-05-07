#coding:utf-8

class TestPluginMethod(object):
    def __init__(self):
        self.called = False

    def __call__(self, *args, **kwargs):
        self.called = True


preBuildPage = TestPluginMethod()  # site, page, context, data
postBuildPage = TestPluginMethod()  # page / site, page, context, data
preBuild = TestPluginMethod()  # site
postBuild = TestPluginMethod()  # site
preDeploy = TestPluginMethod()  # site
postDeploy = TestPluginMethod()  # site
preDeployFile = TestPluginMethod()  # file