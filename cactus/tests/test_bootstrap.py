#coding:utf-8
import os
import shutil
import tarfile
import tempfile
import unittest
import zipfile
import threading
import random

from six.moves import BaseHTTPServer, SimpleHTTPServer, xrange

from cactus.bootstrap import bootstrap
from cactus.tests import BaseBootstrappedTestCase
from cactus.utils.filesystem import fileList


def ArchiveServerHandlerFactory(archive_path):
    class ArchiveHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def do_GET(self):
            """
            Reply with the archive.
            """
            self.send_response(200)
            self.end_headers()
            with open(archive_path, 'rb') as f:
                self.copyfile(f, self.wfile)

        def log_request(self, code='-', size='-'):
            """
            Discard log requests to clear up test output.
            """
            return

    return ArchiveHandler


class TestFolderBootstrap(BaseBootstrappedTestCase):
    def test_bootstrap(self):
        self.assertEqual(
            sorted(fileList(self.path, relative=True)),
            sorted(fileList("cactus/tests/data/skeleton", relative=True)),
        )


class TestCactusPackageBootstrap(BaseBootstrappedTestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, 'test')
        self.clear_django_settings()
        bootstrap(self.path)

    def test_bootstrap(self):
        self.assertEqual(
            sorted(fileList(self.path, relative=True)),
            sorted(fileList("cactus/skeleton", relative=True)),
        )


class BaseTestArchiveBootstrap(object):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.path = os.path.join(self.test_dir, 'test')
        self.skeleton_path = "cactus/skeleton"
        self.archive_path = os.path.join(self.test_dir, "archive")

        with open(self.archive_path, "wb") as f:
            self.make_archive(f)

    def make_archive(self, f):
        raise NotImplementedError()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_file(self):
        # Test
        bootstrap(self.path, self.archive_path)

        self.assertEqual(
            sorted(fileList(self.path, relative=True)),
            sorted(fileList(self.skeleton_path, relative=True)),
        )

    def test_url(self):
        archive_path = self.archive_path

        port = random.choice(xrange(7000, 10000))

        server_address = ("127.0.0.1", port)
        httpd = BaseHTTPServer.HTTPServer(server_address, ArchiveServerHandlerFactory(archive_path))
        t = threading.Thread(target=httpd.serve_forever)
        t.start()

        bootstrap(self.path, "http://127.0.0.1:%s" % port)
        httpd.shutdown()

        self.assertEqual(
            sorted(fileList(self.path, relative=True)),
            sorted(fileList(self.skeleton_path, relative=True)),
        )


class ZIPTestArchiveBootstrap(BaseTestArchiveBootstrap, unittest.TestCase):
    """
    Test ZIP archive support
    """
    def make_archive(self, f):
        archive = zipfile.ZipFile(f, mode="w")
        for resource in fileList(self.skeleton_path, relative=True):
            archive.write(os.path.join(self.skeleton_path, resource), resource)
        archive.close()


class TARTestArchiveBootstrap(BaseTestArchiveBootstrap, unittest.TestCase):
    """
    Test TAR archive support
    """
    def make_archive(self, f):
        archive = tarfile.open(f.name, fileobj=f, mode="w")
        for resource in fileList(self.skeleton_path, relative=True):
            archive.add(os.path.join(self.skeleton_path, resource), resource)
        archive.close()
