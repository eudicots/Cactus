#coding:utf-8
import logging
import socket

from boto.exception import S3ResponseError

from cactus.deployment.file import BaseFile
from cactus.utils.helpers import CaseInsensitiveDict
from cactus.utils.network import retry
from cactus.utils.url import getURLHeaders


logger = logging.getLogger(__name__)


class S3File(BaseFile):
    def __init__(self, engine, path):
        super(S3File, self).__init__(engine, path)
        self.extra_headers = CaseInsensitiveDict()

    def get_headers(self):
        headers = CaseInsensitiveDict()
        headers['Cache-Control'] = 'max-age={0}'.format(self.cache_control)
        if self.content_encoding is not None:
            headers['Content-Encoding'] = self.content_encoding
        headers.update(self.extra_headers)
        return headers

    def remote_url(self):
        return 'http://%s/%s' % (self.engine.site.config.get('aws-bucket-website'), self.url)

    def remote_changed(self):
        remote_headers = dict((k, v.strip('"')) for k, v in getURLHeaders(self.remote_url()).items())
        local_headers = self.get_headers()
        local_headers['etag'] = self.payload_checksum
        for k, v in local_headers.items():  # Don't check AWS' own headers.
            if remote_headers.get(k) != v:
                return True
        return False

    @retry((S3ResponseError, socket.error), tries=5, delay=1, backoff=2)
    def do_upload(self):
        
        # Show progress if the file size is big
        progressCallback = None
        # progressCallbackCount = int(len(self.payload()) / (1024 * 1024))


        # if len(self.payload()) > self.PROGRESS_MIN_SIZE:
        #     def progressCallback(current, total):
        #         if current > self.lastUpload:
        #             uploadPercentage = (float(current) / float(total)) * 100
        #             logger.info('+ %s upload progress %.1f%%' % (self.url, uploadPercentage))
        #             self.lastUpload = current
        
        progressCallbackCount = len(self.payload()) / (1024 * 10) # Every byte

        def progressCallback(current, total):
            self.total_bytes_uploaded = current
            logger.signal("deploy.progress", {
                "progress": float(self.engine.total_bytes_uploaded()) / float(self.engine.total_bytes()),
                "fileName": ""
            })

            logger.info('+ %s upload progress %.1f%%', 
                self.url, float(current) / float(total) * 100)


        key = self.engine.bucket.new_key(self.url)
        
        if self.content_type:
            key.content_type = self.content_type  # We don't it need before (local headers only)
        key.md5 = self.payload_checksum   # In case of a flaky network
        key.set_contents_from_string(self.payload(),
            headers=self.get_headers(),
            policy='public-read',
            cb=progressCallback,
            num_cb=progressCallbackCount)
