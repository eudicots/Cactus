#coding:utf-8
import os
import shutil
import copy
from cactus import Site

from cactus.static.external import ExternalProcessor, ExternalFailure
from cactus.static import optimizers, processors
from cactus.tests import SiteTest


class TestExternal(ExternalProcessor):
    runs = []

    def run(self):
        TestExternal.runs.append(self)
        return super(TestExternal, self).run()


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


class UnrelatedOptimizer(DummyExternal):
    supported_extensions = ('aaa',)
    output_extension = 'bbb'



class TestStaticExternals(SiteTest):
    """
    Test that externals are called properly, and that exceptions are handled properly.
    """
    def setUp(self):
        super(TestStaticExternals, self).setUp()

        self._processors = copy.copy(processors.processors)
        self._optimizers = copy.copy(optimizers.optimizers)

        self._clear(processors.processors)
        self._clear(optimizers.optimizers)

        self.conf.set('optimize', ['src', 'dst'])
        self.conf.write()

        self.site = Site(self.path, self.config_path)

        self.dummy_static = 'test.src'
        open(os.path.join(self.site.static_path, self.dummy_static), 'w')

        TestExternal.runs = []

    def tearDown(self):
        optimizers.optimizers = self._optimizers
        processors.processors = self._processors

    def _clear(self, l):
        """
        Clear a list in place, to easily mock it.
        """
        while 1:
            try:
                l.pop()
            except IndexError:
                break

    def test_critical(self):
        """
        Test that failures on critical processors are escalated
        """
        processors.processors.append(DummyCriticalFailingProc)
        self.assertRaises(ExternalFailure, self.site.build)

    def test_non_critical(self):
        """
        Test that failures on non-critical processors are ignored
        """
        processors.processors.append(DummyOptionalFailingProc)
        self.site.build()

    def test_run(self):
        """
        Test that processors and optimizers run
        """
        processors.processors.append(DummyProc)
        optimizers.optimizers.append(DummyOptimizer)
        optimizers.optimizers.append(UnrelatedOptimizer)
        self.site.build()

        self.assertEqual(2, len(TestExternal.runs))
        proc, opti = TestExternal.runs

        self.assertIsInstance(proc, DummyProc)
        self.assertIsInstance(opti, DummyOptimizer)

    def test_extensions(self):
        """
        Test that processors extensions are taken into account
        """
        processors.processors.append(ExtensionDummyProc)
        self.site.build()

        for static in self.site.static():
            if static.src_filename == self.dummy_static:
                self.assertEqual(static.final_extension, ExtensionDummyProc.output_extension)
                break
        else:
            self.fail("Did not find {0}".format(self.dummy_static))