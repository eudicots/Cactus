#coding:utf-8
import platform


_platform = platform.system()


if _platform in ("Darwin", "Linux"):
    SASS_PATH = "sass"
elif _platform in ("Windows",):
    SASS_PATH = "sass.bat"
else:
    #TODO: Java?
    pass

