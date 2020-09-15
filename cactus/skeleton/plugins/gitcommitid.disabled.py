import subprocess



KEY = 'GIT_COMMITID'

def commitid():
    command = 'git log -1 --format="%H"'
    print("run command [%s]" % command)
    result = subprocess.check_output(command, shell=True)
    result = result.rstrip('\n')
    print("result command [%s]" % result)
    return result


mycommitid = "undefined"

def preBuildPage(page, context, data):
    global mycommitid
    if (mycommitid == "undefined"):
        mycommitid = commitid()

    context[KEY] = mycommitid
    return context, data