import os
import sys

import SimpleHTTPServer
import SocketServer

import mime

# See: https://github.com/koenbok/Cactus/issues/8
# class Server(SocketServer.ForkingMixIn, SocketServer.TCPServer):
#	allow_reuse_address = True

class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	allow_reuse_address = True

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
		
		f = None
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
		
		# Last-Modified", self.date_time_string(fs.st_mtime)
		
		return self.send_content(200, headers, f)
	
	def send_content(self, code, headers, fileHandler):
		
		self.send_response(code)
		
		for key, value in headers.iteritems():
			self.send_header(key, value)
		
		self.end_headers()
		
		return fileHandler
	
	def log_message(self, format, *args):
		sys.stdout.write("%s\n" % format%args)

	def log_request(self, code='', size=''):
		try:
			self.log_message('%s %s %s', str(code), 
				self.requestline.split(' ')[0], 
				self.requestline.split(' ')[1])
		except:
			pass

	def guess_type(self, path):
		return mime.guess(path)
