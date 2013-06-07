import os
import logging
import hashlib
import socket
from cactus.utils.file import compressString, fileSize
from cactus.utils.helpers import CaseInsensitiveDict, memoize
from cactus.utils.network import retry
from cactus.utils.url import getURLHeaders
import mime
import copy


class File(object):
    DEFAULT_CACHE_EXPIRATION = 60 * 60 * 24 * 7  # One week
    COMPRESS_TYPES = ['html', 'css', 'js', 'txt', 'xml']
    PROGRESS_MIN_SIZE = (1024 * 1024) / 2  # 521 kb

    def __init__(self, site, path):
        self.site = site
        self.path = path

        self.force_refresh = False
        self._is_compressed = None

    def prepare(self):
        """
        Prepare the file for upload
        """
        self.payload()  # Decide whether we'll compress or not.
        self.lastUpload = 0

    def cache_duration(self):
        if self.site.cache_duration is not None:
            return self.site.cache_duration
        return self.DEFAULT_CACHE_EXPIRATION

    def data(self):
        with open(os.path.join(self.site.path, '.build', self.path)) as f:
            return f.read()

    def payload(self):
        """
        The representation of the data that should be uploaded to the
        server. This might be compressed based on the content type and size.
        """
        if not hasattr(self, '_payload'):
            raw_data = self.data()

            if self.extension() in self.COMPRESS_TYPES:
                compressed_data = compressString(raw_data)

                if len(compressed_data) < len(raw_data):
                    self._is_compressed = True
                    self._payload = compressed_data
                    return self._payload

            self.is_compressed = False
            self._payload = raw_data

        return self._payload

    @property
    def is_compressed(self):
        if self._is_compressed is None:
            raise Exception('Compression not defined yet!')
        return self._is_compressed

    @is_compressed.setter
    def is_compressed(self, boolean):
        self._is_compressed = boolean

    def checksum(self):
        """
        An amazon compatible md5 of the payload data.
        """
        return hashlib.md5(self.payload()).hexdigest()

    def remoteChecksum(self):
        return getURLHeaders(self.remoteURL()).get('etag', '').strip('"')

    def remoteURL(self):
        return 'http://%s/%s' % (self.site.config.get('aws-bucket-website'), self.path)

    def extension(self):
        return os.path.splitext(self.path)[1].strip('.').lower()

    def shouldCompress(self):

        if not self.extension() in self.COMPRESS_TYPES:
            return False

        if len(self.data()) < self.COMPRESS_MIN_SIZE:
            return False

        return True

    def changed(self):
        """
        Check whether a plugin set the force refresh file, otherwise,
        check headers.
        """
        if self.force_refresh:
            return True

        remote_headers = {k: v.strip('"') for k, v in getURLHeaders(self.remoteURL()).items()}
        local_headers = copy.copy(self.headers)
        local_headers['etag'] = self.checksum()
        for k, v in local_headers.items():  # Don't check AWS' own headers.
            if remote_headers.get(k) != v:
                return True
        return False

    @retry(socket.error, tries=5, delay=3, backoff=2)
    def upload(self, bucket):
        self.prepare()

        self.headers = CaseInsensitiveDict((('Cache-Control', 'max-age=%s' % self.cache_duration()),))

        if self.is_compressed:
            self.headers['Content-Encoding'] = 'gzip'

        self.site.plugin_manager.preDeployFile(self)

        changed = self.changed()

        if changed:

            # Show progress if the file size is big
            progressCallback = None
            progressCallbackCount = int(len(self.payload()) / (1024 * 1024))

            if len(self.payload()) > self.PROGRESS_MIN_SIZE:
                def progressCallback(current, total):
                    if current > self.lastUpload:
                        uploadPercentage = (float(current) / float(total)) * 100
                        logging.info('+ %s upload progress %.1f%%' % (self.path, uploadPercentage))
                        self.lastUpload = current

            # Create a new key from the file path and guess the mime type
            key = bucket.new_key(self.path)
            mimeType = mime.guess(self.path)

            if mimeType:
                key.content_type = mimeType

            # Upload the data
            key.set_contents_from_string(self.payload(), self.headers,
                                         policy='public-read',
                                         cb=progressCallback,
                                         num_cb=progressCallbackCount)

        op1 = '+' if changed else '-'
        op2 = ' (%s compressed)' % (fileSize(len(self.payload()))) if self.is_compressed else ''

        logging.info('%s %s - %s%s' % (op1, self.path, fileSize(len(self.data())), op2))

        return {'changed': changed, 'size': len(self.payload())}

    def __repr__(self):
        return '<File: {0}>'.format(self.path)
