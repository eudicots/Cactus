#coding:utf-8
import os
import io
import logging

from cactus import mime
from cactus.utils import ipc
from cactus.utils.file import compressString, fileSize
from cactus.utils.helpers import memoize, checksum
from cactus.utils.url import path_to_url


logger = logging.getLogger(__name__)


class BaseFile(object):
    DEFAULT_CACHE_EXPIRATION = 60 * 60 * 24 * 7  # One week
    MAX_CACHE_EXPIRATION = 60 * 60 * 24 * 365 # 1 Year (for cached)
    PROGRESS_MIN_SIZE = (1024 * 1024) / 2  # 521 kb

    def __init__(self, engine, path):
        self.engine = engine
        self.path = path

        self.force_refresh = False
        self._is_compressed = None

        self.total_bytes = len(self.payload())
        self.total_bytes_uploaded = 0

    def prepare(self):
        """
        Prepare the file for upload
        """
        payload = self.payload()  # Decide whether we'll compress or not.
        self.payload_checksum = checksum(payload)
        self.lastUpload = 0

    @property
    def url(self):
        """
        We must use this when deploying, otherwise the paths will be broken when
        deploying from Windows
        """
        return path_to_url(self.path)

    @memoize
    def data(self):
        with io.FileIO(os.path.join(self.engine.site.build_path, self.path), 'r') as f:
            return f.read()

    def payload(self):
        """
        The representation of the data that should be uploaded to the
        server. This might be compressed based on the content type and size.
        """
        if not hasattr(self, '_payload'):
            raw_data = self.data()

            if self.extension() in self.engine.site.compress_extensions:
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
        assert self._is_compressed is not None, "Compression is not defined yet!"
        return self._is_compressed

    @is_compressed.setter
    def is_compressed(self, boolean):
        self._is_compressed = boolean

    @property
    def is_fingerprinted(self):
        """
        Lazy implementation (needs to be fixed); we'll re-fingerprint the file
        and check whether that happens to be in the filename.
        """
        #TODO: FixMe!
        return checksum(self.data()) in self.path

    def extension(self):
        return os.path.splitext(self.path)[1].strip('.').lower()

    @property
    def content_type(self):
        """
        Return the content type for this object
        """
        content_type = mime.guess(self.path)

        if not content_type:
            return None

        if content_type == "text/html":
            content_type = "{0}; charset=utf-8".format(content_type)

        return content_type

    def must_refresh(self):
        if self.force_refresh:
            return True

        return self.remote_changed()

    def upload(self):

        self.prepare()

        # Plugins may actually update those values afterwards
        self.cache_control = self.MAX_CACHE_EXPIRATION if self.is_fingerprinted else self.DEFAULT_CACHE_EXPIRATION
        self.content_encoding = 'gzip' if self.is_compressed else None
        self.content_length = len(self.payload())

        self.engine.site.plugin_manager.preDeployFile(self)

        remote_changed = self.remote_changed()

        if remote_changed:
            self.do_upload()

        self.total_bytes_uploaded = self.total_bytes

        op1 = '+' if remote_changed else '-'
        op2 = ' (%s compressed)' % (fileSize(len(self.payload()))) if self.is_compressed else ''

        # logger.warning("deploy.progress %s", self.engine.progress())

        ipc.signal("deploy.progress", {
            "progress": self.engine.progress(),
            "fileName": self.path
        })

        logger.info('%s %s - %s%s' % (op1, self.path, fileSize(len(self.data())), op2))

        return {'changed': remote_changed, 'size': len(self.payload())}

    def __repr__(self):
        return '<File: {0}>'.format(self.path)

    def remote_changed(self):
        """
        Did the file change when compared to the remote?
        :rtype: bool
        """
        raise NotImplementedError()

    def do_upload(self):
        """
        Actually upload the file to the remote
        """
        raise NotImplementedError()
