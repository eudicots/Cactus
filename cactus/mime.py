import os
import mimetypes

MIMETYPE_MAP = {
	'.js': 'text/javascript',
	'.mov': 'video/quicktime',
	'.mp4': 'video/mp4',
	'.m4v': 'video/x-m4v',
	'.3gp': 'video/3gpp',
	'.woff': 'application/font-woff',
}

def guess(path):
	
	base, ext = os.path.splitext(path)
	
	if ext.lower() in MIMETYPE_MAP:
		return MIMETYPE_MAP[ext.lower()]
	
	suggested = mimetypes.guess_type(path)
	
	if suggested:
		return suggested[0]
	
	return 'application/octet-stream'
