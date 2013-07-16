#coding:utf-8
import os

from cactus.tests.deployment import BaseDeploymentTestCase, DummyDeploymentEngine, DummySite, DummyUI, DummyFile


class FileChangedTestCase(BaseDeploymentTestCase):
    def setUp(self):
        super(FileChangedTestCase, self).setUp()
        self.ui = DummyUI()
        self.site = DummySite(self.test_dir, self.ui)
        self.engine = DummyDeploymentEngine(self.site)
        with open(os.path.join(self.test_dir, "123.html"), "w") as f:
            f.write("Hello!")

    def test_file_unchanged(self):
        """
        Test that we don't attempt to deploy unchanged files
        """
        class TestFile(DummyFile):
            def remote_changed(self):
                super(TestFile, self).remote_changed()
                return False

        self.engine.FileClass = TestFile
        self.engine.deploy()
        files = self.engine.created_files
        self.assertEqual(1, len(files))

        f = files[0]

        self.assertEqual(1, f.remote_changed_calls)
        self.assertEqual(0, f.do_upload_calls)


    def test_file_changed(self):
        """
        Test that we deploy files that changed
        """
        class TestFile(DummyFile):
            def remote_changed(self):
                super(TestFile, self).remote_changed()
                return True

        self.engine.FileClass = TestFile
        self.engine.deploy()
        files = self.engine.created_files
        self.assertEqual(1, len(files))

        f = files[0]

        self.assertEqual(1, f.remote_changed_calls)
        self.assertEqual(1, f.do_upload_calls)
