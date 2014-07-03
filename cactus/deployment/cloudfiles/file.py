#coding:utf-8

from cactus.deployment.file import BaseFile
from cactus.utils.helpers import CaseInsensitiveDict


class CloudFilesFile(BaseFile):
    def remote_changed(self):
        obj = self.engine.bucket.get_object(self.url)
        #TODO: Headers
        return obj.etag != self.payload_checksum

    def get_headers(self):
        headers = CaseInsensitiveDict()
        for k in ("Cache-Control", "X-TTL"):
            headers[k] = 'max-age={0}'.format(self.cache_control)
        if self.content_encoding is not None:
            headers['Content-Encoding'] = self.content_encoding
        return headers

    def do_upload(self):
        obj = self.engine.bucket.store_object(self.url, self.payload(), content_type=self.content_type,
                                              etag=self.payload_checksum, content_encoding=self.content_encoding,)
        obj.set_metadata(self.get_headers())
