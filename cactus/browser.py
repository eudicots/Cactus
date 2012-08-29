import subprocess
import platform

s1 = """
if application "Google Chrome" is running then
	tell application "Google Chrome"
		set windowsList to windows as list
		repeat with currWindow in windowsList
			set tabsList to currWindow's tabs as list
			repeat with currTab in tabsList
				if "%s" is in currTab's URL then execute currTab javascript "%s"
			end repeat
		end repeat
	end tell
end if
"""

s2 = """
if application "Safari" is running then
	tell application "Safari"
		if (count of windows) is greater than 0 then
			set windowsList to windows as list
			repeat with currWindow in windowsList
				set tabsList to currWindow's tabs as list
				repeat with currTab in tabsList
					if "%s" is in currTab's URL then tell currTab to do JavaScript "%s"
				end repeat
			end repeat
		end if
	end tell
end if
"""

def applescript(input):
	
	# Bail if we're not on mac os for now
	if platform.system() != "Darwin":
		return
		
	return subprocess.check_output("osascript<<END%sEND" % input, shell=True)

def _insertJavascript(urlMatch, js):

	try: applescript(s1 % (urlMatch, js))
	except Exception, e: pass

	try: applescript(s2 % (urlMatch, js))
	except Exception, e: pass

def browserReload(url):
	_insertJavascript(url, "window.location.reload()")

def browserReloadCSS(url):
	_insertJavascript(url, "var links = document.getElementsByTagName('link'); for (var i = 0; i < links.length;i++) { var link = links[i]; if (link.rel === 'stylesheet') {link.href += '?'; }}")

