#coding:utf-8
import os
import shutil
from cactus.static.external.exceptions import ExternalFailure

from cactus.static.external import External
from cactus.tests import SiteTestCase


class TestExternal(External):
    runs = []

    def run(self):
        out = super(TestExternal, self).run()
        if self.accepted():
            TestExternal.runs.append(self)
        return out


class DummyCriticalFailingProc(TestExternal):
    supported_extensions = ('src',)
    output_extension = 'dst'
    critical = True

    def _run(self):
        raise OSError('Error.')


class DummyOptionalFailingProc(TestExternal):
    supported_extensions = ('src',)
    output_extension = 'dst'
    critical = False

    def _run(self):
        raise OSError('Error.')


class DummyExternal(TestExternal):
    supported_extensions = ('src',)
    critical = False

    def _run(self):
        shutil.move(self.src, self.dst)


class ExtensionDummyProc(DummyExternal):
    supported_extensions = ('src',)
    output_extension = 'blah'


class DummyProc(DummyExternal):
    output_extension = 'dst'


class DummyOptimizer(DummyExternal):
    supported_extensions = ('dst',)
    output_extension = 'dst'


class SourceOptimizer(DummyExternal):
    supported_extensions = ('src',)
    output_extension =  'src'


class UnrelatedOptimizer(DummyExternal):
    supported_extensions = ('aaa',)
    output_extension = 'bbb'


class DiscardingProcessor(DummyProc):
    def _run(self):
        self.discard()



class TestStaticExternals(SiteTestCase):
    """
    Test that externals are called properly, and that exceptions are handled properly.
    """
    def get_config_for_test(self):
        return {"optimize": ["src", "dst"]}

    def setUp(self):
        super(TestStaticExternals, self).setUp()
        self.site.external_manager.clear()

        # Write an empty file
        self.dummy_static = 'test.src'
        open(os.path.join(self.site.static_path, self.dummy_static), 'wb')

        TestExternal.runs = []

    def test_critical(self):
        """
        Test that failures on critical processors are escalated
        """
        self.site.external_manager.register_processor(DummyCriticalFailingProc)
        self.assertRaises(ExternalFailure, self.site.build)

    def test_non_critical(self):
        """
        Test that failures on non-critical processors are ignored
        """
        self.site.external_manager.register_processor(DummyOptionalFailingProc)
        self.site.build()

    def test_deregister(self):
        """
        Test that we can de-register a processor.
        """
        self.site.external_manager.register_processor(DummyCriticalFailingProc)
        self.assertRaises(ExternalFailure, self.site.build)
        self.site.external_manager.deregister_processor(DummyCriticalFailingProc)
        self.site.build()

    def test_run(self):
        """
        Test that processors and optimizers run
        """
        self.site.external_manager.register_processor(DummyProc)
        self.site.external_manager.register_optimizer(DummyOptimizer)
        self.site.external_manager.register_optimizer(UnrelatedOptimizer)
        self.site.build()

        self.assertEqual(2, len(TestExternal.runs))
        proc, opti = TestExternal.runs

        self.assertIsInstance(proc, DummyProc)
        self.assertIsInstance(opti, DummyOptimizer)

    def test_extensions(self):
        """
        Test that processors extensions are taken into account
        """
        self.site.external_manager.register_processor(ExtensionDummyProc)
        self.site.build()

        for static in self.site.static():
            if static.src_filename == self.dummy_static:
                self.assertEqual(static.final_extension, ExtensionDummyProc.output_extension)
                break
        else:
            self.fail("Did not find {0}".format(self.dummy_static))

    def test_discard(self):
        """
        Test that we discard files properly
        """
        self.site.external_manager.register_processor(DiscardingProcessor)
        self.site.external_manager.register_optimizer(SourceOptimizer)

        self.site.build()

        self.assertEqual(0, len(TestExternal.runs))  # Check that our optimizer does not run
        self.assertFileDoesNotExist(os.path.join(self.site.build_path, "static", "test.dst"))
        self.assertFileDoesNotExist(os.path.join(self.site.build_path, "static", "test.src"))

        for static in self.site.static():
            if static.src_filename == self.dummy_static:
                self.assertTrue(static.discarded)
