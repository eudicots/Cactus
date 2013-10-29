import os
import sys
import logging
import errno

import SimpleHTTPServer
import SocketServer

import mime

logger = logging.getLogger(__name__)

# See: https://github.com/koenbok/Cactus/issues/8
# class Server(SocketServer.ForkingMixIn, SocketServer.TCPServer):
#	allow_reuse_address = True

class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer, object):
    
    allow_reuse_address = True

    def handle_error(self, request, client_address):

        exc_type, exc_obj, exc_tb = sys.exc_info()
        
        # Don't complain about agressive browsers all the time
        if "Broken pipe" in exc_obj:
            return

        logger.info("handle_error", request, exc_obj);
        
        return super(Server, self).handle_error(request, client_address)

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """

        path = self.translate_path(self.path)

        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
                    # else:
                    # 	return self.list_directory(path)

        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')

        except IOError:

            errorPagePath = self.translate_path('/error.html')

            if os.path.exists(errorPagePath):
                return self.send_content(404,
                    {"Content-type": "text/html"}, 
                    open(errorPagePath, 'rb'))
            else:
                self.send_error(404, "File not found")
            return None

        fs = os.fstat(f.fileno())
        tp = self.guess_type(path)

        headers = {
            "Content-type": tp,
            "Content-Length": str(fs[6]),
            "Cache-Control": "no-cache, must-revalidate",
        }
        
        # It would be great if this worked reliably, but for now we use no caching
        # Last-Modified", self.date_time_string(fs.st_mtime)

        return self.send_content(200, headers, f)

    def send_content(self, code, headers, fileHandler):

        self.send_response(code)

        for key, value in headers.iteritems():
            self.send_header(key, value)

        self.end_headers()

        return fileHandler

    def log_message(self, fmt, *args):
        
        # Be less noisy
        if "timed out" in fmt:
            return
        
        logger.info(fmt, *args)

    def log_request(self, code = '', size = ''):
        
        action = self.requestline.split(' ')[0]
        path = self.requestline.split(' ')[1]
        
        if code in [200, 301]:
            logger.info('%s %s %s', str(code), action, path)
        else:
            logger.warning('%s %s %s', str(code), action, path)

    def guess_type(self, path):
        return mime.guess(path)
