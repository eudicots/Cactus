#coding:utf-8
import filecmp
import logging
import os
import shutil

from cactus.deployment.file import BaseFile

logger = logging.getLogger(__name__)


class LocalFile(BaseFile):
    source_path = None
    target_path = None

    def __init__(self, engine, path):
        super(LocalFile, self).__init__(engine, path)
        self.target_path = '%s/%s' % (self.engine.target_directory, path)
        self.source_path = os.path.join(self.engine.site.build_path, path)

    def remote_changed(self):
        if os.path.exists(self.target_path):
            return not filecmp.cmp(self.source_path, self.target_path)
        else:
            return True

    def do_upload(self):
        if not os.path.exists(os.path.dirname(self.target_path)):
            try:
                os.makedirs(os.path.dirname(self.target_path))
            except OSError:
                # Racy directory creation. Subsequent copy may still fail
                pass

        shutil.copyfile(self.source_path, self.target_path)

