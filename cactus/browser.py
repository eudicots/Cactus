import subprocess
import platform

s1 = """
tell application "Google Chrome"
	set windowsList to windows as list
	repeat with currWindow in windowsList
		set tabsList to currWindow's tabs as list
		repeat with currTab in tabsList
			if "%s" is in currTab's URL then execute currTab javascript "%s"
		end repeat
	end repeat
end tell
"""

s2 = """
tell application "Safari"
	if (count of windows) is greater than 0 then
		set windowsList to windows as list
		repeat with currWindow in windowsList
			set tabsList to currWindow's tabs as list
			repeat with currTab in tabsList
				if "%s" is in currTab's URL then 
					tell currTab to do JavaScript "%s"
				end if
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
		var re = new RegExp("([?|&])" + key + "=.*?(&|$)", "i");
		separator = uri.indexOf('?') !== -1 ? "&" : "?";
		
		if (uri.match(re)) {
			return uri.replace(re, '$1' + key + "=" + value + '$2');
		} else {
			return uri + separator + key + "=" + value;
		}
	}
	
	var links = document.getElementsByTagName('link'); 
	
	for (var i = 0; i < links.length;i++) { 
	
		var link = links[i]; 
	
		if (link.rel === 'stylesheet') {
			link.href = updateQueryStringParameter(link.href, 'cactus.reload', new Date().getTime())
		}
	}
})()
"""

def applescript(input):
	
	# Bail if we're not on mac os for now
	if platform.system() != "Darwin":
		return
	
	command = "osascript<<END%sEND" % input
	return subprocess.check_output(command, shell=True)

def _insertJavascript(urlMatch, js):
	
	apps = appsRunning(['Safari', 'Google Chrome'])
	
	if apps['Google Chrome']:
		try: applescript(s1 % (urlMatch, js))
		except Exception, e: pass
	
	if apps['Safari']:
		try: applescript(s2 % (urlMatch, js))
		except Exception, e: pass

def browserReload(url):
	_insertJavascript(url, s3)

def browserReloadCSS(url):
	_insertJavascript(url, s4)

def appsRunning(l):
	psdata = subprocess.check_output(['ps aux'], shell=True)
	retval = {}
	for app in l: retval[app] = app in psdata
	return retval
