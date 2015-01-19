#coding:utf-8

class TestPluginMethod(object):
    def __init__(self, fn=None):
        self.calls = []
        self.fn = fn

    def __call__(self, *args, **kwargs):
        self.calls.append({'args': args, 'kwargs': kwargs})
        if self.fn is not None:
            return self.fn(*args, **kwargs)


preBuildPage = TestPluginMethod(lambda page, context, data: (context, data,))  # site, page, context, data
postBuildPage = TestPluginMethod()  # page / site, page, context, data
preBuild = TestPluginMethod()  # site
postBuild = TestPluginMethod()  # site
preDeploy = TestPluginMethod()  # site
postDeploy = TestPluginMethod()  # site
preDeployFile = TestPluginMethod()  # file

ORDER = 2
