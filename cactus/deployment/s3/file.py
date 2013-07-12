#coding:utf-8
import copy
import logging
import socket
from boto.exception import S3ResponseError
from cactus.deployment.file import BaseFile
from cactus.utils.network import retry
from cactus.utils.url import getURLHeaders


class S3File(BaseFile):
    def remoteURL(self):
        return 'http://%s/%s' % (self.site.config.get('aws-bucket-website'), self.path)

    def remote_changed(self):
        """
        Check whether a plugin set the force refresh file, otherwise,
        check headers.
        """
        remote_headers = dict((k, v.strip('"')) for k, v in getURLHeaders(self.remoteURL()).items())
        local_headers = copy.copy(self.headers)
        local_headers['etag'] = self.payload_checksum
        for k, v in local_headers.items():  # Don't check AWS' own headers.
            if remote_headers.get(k) != v:
                return True
        return False

    @retry((S3ResponseError, socket.error), tries=5, delay=3, backoff=2)
    def do_upload(self):
        # Show progress if the file size is big
        progressCallback = None
        progressCallbackCount = int(len(self.payload()) / (1024 * 1024))

        if len(self.payload()) > self.PROGRESS_MIN_SIZE:
            def progressCallback(current, total):
                if current > self.lastUpload:
                    uploadPercentage = (float(current) / float(total)) * 100
                    logging.info('+ %s upload progress %.1f%%' % (self.path, uploadPercentage))
                    self.lastUpload = current


        key = self.engine.bucket.new_key(self.path)
        key.content_type = self.content_type  # We don't it need before (local headers only)
        key.md5 = self.payload_checksum   # In case of a flaky network
        key.set_contents_from_string(self.payload(),
            headers=self.headers,
            policy='public-read',
            cb=progressCallback,
            num_cb=progressCallbackCount)
