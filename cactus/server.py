import os
import sys
import logging
import threading
import mimetypes
import itertools

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

logger = logging.getLogger(__name__)

from cactus import mime

TEMPLATES = {}


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        if self not in self.application._socketHandlers:
            self.application._socketHandlers.append(self)

    def on_close(self):
        if self in self.application._socketHandlers:
            self.application._socketHandlers.remove(self)

    def on_message(self, msg):
        pass


class ShutdownHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_callback(lambda x: x.stop(), ioloop)


class StaticHandler(tornado.web.StaticFileHandler):

    @classmethod
    def get_append(cls, abspath):

        mime_type, encoding = mimetypes.guess_type(abspath)

        if mime_type == "text/html":
            return TEMPLATES["script"]

        return ""

    @classmethod
    def get_content(cls, abspath, start=None, end=None):
        data = super(StaticHandler, cls).get_content(abspath, start=start, end=end)
        return itertools.chain(data, [cls.get_append(abspath)])

    def get_content_size(self):
        return super(StaticHandler, self).get_content_size() + len(self.get_append(self.absolute_path))

    # Always be not caching
    def should_return_304(self):
        return False

    def get_content_type(self):
        return mime.guess(self.absolute_path)

    def write_error(self, status_code, **kwargs):
        # Special case handling for 404: try to find one of the error pages,
        # which might be in error.html or error/index.html depending on
        # whether prettifying was enabled.
        if status_code == 404:
            for path in ["error.html", "error/index.html"]:
                try:
                    return self.render(path)
                except IOError:
                    continue

        return super(StaticHandler, self).write_error(status_code, **kwargs)

    def log_request(self, handler):
        pass


class StaticSingleFileHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header("Content-Type", mime.guess("file.js"))
        self.finish(TEMPLATES["js"])


class WebServer(object):

    def __init__(self, path, port=8080):

        self.path = path
        self.port = port

        self.application = tornado.web.Application([
            (r'/_cactus/shutdown', ShutdownHandler),
            (r'/_cactus/ws', WebSocketHandler),
            (r'/_cactus/cactus.js', StaticSingleFileHandler),
            (r'/(.*)', StaticHandler, {'path': self.path, "default_filename": "index.html"}),
        ], template_path=self.path)

        self.application.log_request = lambda x: self._log_request(x)

    def _log_request(self, handler):

        if not isinstance(handler, StaticHandler):
            return

        if handler.get_status() < 400:
            log_method = logging.info
        elif handler.get_status() < 500:
            log_method = logging.warning
        else:
            log_method = logging.error

        log_method("%d %s %s", handler.get_status(), handler.request.method, handler.request.uri)


    def start(self):
        self.application._socketHandlers = []

        self._server = tornado.httpserver.HTTPServer(self.application)
        self._server.listen(self.port)

        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        pass

    def publish(self, message):
        for ws in self.application._socketHandlers:
            ws.write_message(message)

    def reloadPage(self):
        self.publish("reloadPage")

    def reloadCSS(self):
        self.publish("reloadCSS")


TEMPLATES["script"] = """

<!-- Automatically inserted by Cactus. Needed for auto refresh. This will be gone when you deploy -->
<script src="/_cactus/cactus.js"></script>
"""

TEMPLATES["js"] = """
(function() {

function reloadPage() {
    window.location.reload()
}

function reloadCSS() {
    function updateQueryStringParameter(uri, key, value) {

        var re = new RegExp("([?|&])" + key + "=.*?(&|$)", "i");
        separator = uri.indexOf("?") !== -1 ? "&" : "?";

        if (uri.match(re)) {
            return uri.replace(re, "$1" + separator + key + "=" + value + "$2");
        } else {
            return uri + separator + key + "=" + value;
        };
    };

    var links = document.getElementsByTagName("link");

    for (var i = 0; i < links.length;i++) {

        var link = links[i];

        if (link.rel === "stylesheet") {

            // Don"t reload external urls, they likely did not change
            if (
                link.href.indexOf("127.0.0.1") == -1 &&
                link.href.indexOf("localhost") == -1 &&
                link.href.indexOf("0.0.0.0") == -1 &&
                link.href.indexOf(window.location.host) == -1
                ) {
                continue;
            }

            var updatedLink = updateQueryStringParameter(link.href, "cactus.reload", new Date().getTime());

            if (updatedLink.indexOf("?") == -1) {
                updatedLink = updatedLink.replace("&", "?");
            };

            link.href = updatedLink;
        };
    };
};

function startSocket() {

    var MessageActions = {
        reloadPage: reloadPage,
        reloadCSS: reloadCSS
    };

    var socketUrl = "ws://" + window.location.host + "/_cactus/ws"
    var socket = new WebSocket(socketUrl);

    socket.onmessage = function(e) {
        var key = e.data;

        if (MessageActions.hasOwnProperty(key)) {
            MessageActions[key]()
        };
    };
};

startSocket();

})()
"""
