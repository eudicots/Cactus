import subprocess
import platform

s1 = """
set hostLists to %s
tell application "Google Chrome"
    set windowsList to windows as list
    repeat with currWindow in windowsList
        set tabsList to currWindow's tabs as list
        repeat with currTab in tabsList
            repeat with currentHost in hostLists
                if currentHost is in currTab's URL then execute currTab javascript "%s"
            end repeat
        end repeat
    end repeat
end tell
"""

s2 = """
set hostLists to %s
tell application "Safari"
    if (count of windows) is greater than 0 then
        set windowsList to windows as list
        repeat with currWindow in windowsList
            set tabsList to currWindow's tabs as list
            repeat with currTab in tabsList
                repeat with currentHost in hostLists
                    if currentHost is in currTab's URL then
                        tell currTab to do JavaScript "%s"
                    end if
                end repeat
            end repeat
        end repeat
    end if
end tell
"""

s3 = """
window.location.reload()
"""

s4 = """
(function() {
    function updateQueryStringParameter(uri, key, value) {

        var re = new RegExp('([?|&])' + key + '=.*?(&|$)', 'i');
        separator = uri.indexOf('?') !== -1 ? '&' : '?';

        if (uri.match(re)) {
            return uri.replace(re, '$1' + separator + key + '=' + value + '$2');
        } else {
            return uri + separator + key + '=' + value;
        }
    }

    var links = document.getElementsByTagName('link');

    for (var i = 0; i < links.length;i++) {

        var link = links[i];

        if (link.rel === 'stylesheet') {

            // Don't reload external urls, they likely did not change
            if (
                link.href.indexOf('127.0.0.1') == -1 && 
                link.href.indexOf('localhost') == -1 &&
                link.href.indexOf('0.0.0.0') == -1) {
                continue;
            }

            var updatedLink = updateQueryStringParameter(link.href, 'cactus.reload', new Date().getTime());

            // This is really hacky, but needed because the regex gets magically broken by piping it
            // through applescript. This replaces the first occurence of ? with & if there was no &.
            if (updatedLink.indexOf('?') == -1) {
                updatedLink = updatedLink.replace('&', '?');
            }

            link.href = updatedLink;
        }
    }
})()
"""

def applescript(input):

    # Bail if we're not on mac os for now
    if platform.system() != "Darwin":
        return

    command = "osascript<<END%sEND" % input

    try:
        return subprocess.check_call(command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
    except Exception as e:
        pass

    # return subprocess.check_output(command, shell=True)

def _insertJavascript(urlMatch, js):

    apps = appsRunning(['Safari', 'Google Chrome'])

    # urlMatch is a list that needs to be converted to applescript format
    # ["a", "b"] -> {"a", "b"}
    urlMatch = "{\"" + "\",\"".join(urlMatch) + "\"}"

    if apps['Google Chrome']:
        applescript(s1 % (urlMatch, js))

    if apps['Safari']:
        applescript(s2 % (urlMatch, js))

def browserReload(url):
    _insertJavascript(url, s3)

def browserReloadCSS(url):
    _insertJavascript(url, s4)

def appsRunning(l):
    psdata = subprocess.check_output(['ps aux'], shell=True)
    retval = {}
    for app in l: retval[app] = app in psdata
    return retval
