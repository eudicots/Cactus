import os
import mimetypes

MIMETYPE_MAP = {
    '.js':   'text/javascript',
    '.mov':  'video/quicktime',
    '.mp4':  'video/mp4',
    '.m4v':  'video/x-m4v',
    '.3gp':  'video/3gpp',
    '.woff': 'application/font-woff',
    '.eot':  'application/vnd.ms-fontobject',
    '.ttf':  'application/x-font-truetype',
    '.otf':  'application/x-font-opentype',
    '.svg':  'image/svg+xml',
}

MIMETYPE_DEFAULT = 'application/octet-stream'

def guess(path):

    if not path:
        return MIMETYPE_DEFAULT

    base, ext = os.path.splitext(path)

    if ext.lower() in MIMETYPE_MAP:
        return MIMETYPE_MAP[ext.lower()]

    mime_type, encoding = mimetypes.guess_type(path)

    if mime_type:
        return mime_type

    return MIMETYPE_DEFAULT
