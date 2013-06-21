#coding:utf-8
import os
import logging
import tempfile
import shutil

from cactus.utils.compat import StaticCompatibilityLayer
from cactus.utils.file import calculate_file_checksum
from cactus.utils.filesystem import alt_file


class Static(StaticCompatibilityLayer):
    """
    A static resource in the repo
    """

    discarded = False

    def __init__(self, site, path):
        self.site = site

        _static_path, filename = os.path.split(path)

        # Actual source file
        self.src_dir = os.path.join('static', _static_path)
        self.src_filename = filename
        self.src_name, self.src_extension = filename.rsplit('.', 1)

        # Useless we'll crash before.
        # TODO
        assert self.src_extension, "No extension for file?! {0}".format(self.src_name)

        # Do some pre-processing (e.g. optimizations):
        # must be done before fingerprinting
        self._preprocessing_path = self.pre_process()

        # Where the file will have to be referenced in output files

        if self.final_extension in self.site.fingerprint_extensions:
            checksum = calculate_file_checksum(self._preprocessing_path)
            new_name = "{0}.{1}".format(self.src_name, checksum)
        else:
            new_name = self.src_name

        # Path where this file should be referenced in source files
        self.link_url = '/' + os.path.join(self.src_dir, '{0}.{1}'.format(self.src_name, self.final_extension))

        self.final_name = "{0}.{1}".format(new_name, self.final_extension)


    @property
    def full_source_path(self):
        return os.path.join(self.site.path, self.src_dir, self.src_filename)

    @property
    def build_path(self):
        """
        Path where the file should be built to.
        """
        return  os.path.join(self.src_dir, self.final_name)

    @property
    def full_build_path(self):
        """
        Absolute where the file should be built to.
        """
        return os.path.join(self.site.build_path, self.build_path)

    @property
    def final_url(self):
        """
        Path where the file should be referenced in built files
        """
        return "/{0}".format(self.build_path)


    def run_externals(self, current_extension, pre_path, externals):
        """
        Run a set of externals against the file at pre_path
        Only one external will run (the first one to accept the file)

        Return the new extension for the file.
        """
        with alt_file(pre_path) as tmp_file:
            for ExternalClass in externals:
                external = ExternalClass(current_extension, pre_path, tmp_file)
                external.run()

                if external.accepted():
                    return external.output_extension
                elif external.refused():
                    continue
                elif external.discarded():
                    self.discard()
                    break

                raise Exception("External {0} has an unknown status: {1}".format(external, external.status))

            return current_extension

    def pre_process(self):
        """
        Does file pre-processing if required
        """
        self.pre_dir = tempfile.mkdtemp()
        pre_path = os.path.join(self.pre_dir, self.src_filename)

        shutil.copy(self.full_source_path, pre_path)

        # Pre-process
        logging.info('Pre-processing: %s' % self.src_name)

        # Run processors (those might change the extension)
        self.final_extension = self.run_externals(self.src_extension, pre_path, self.site.external_manager.processors)

        # Optimize
        if self.final_extension in self.site.optimize_extensions:
            # Run optimizes and make sure they don't alter the extension
            _ = self.run_externals(self.final_extension, pre_path, self.site.external_manager.optimizers)
            assert self.final_extension == _, "Illegal Optimizer: may not change the extension"

        return pre_path

    def discard(self):
        self.discarded = True  #TODO: Warn on usage of the static!

    def build(self):
        if not self.discarded:
            self.site.plugin_manager.preBuildStatic(self)

            logging.info('Building {0} --> {1}'.format(self.src_name, self.final_url))

            try:
                os.makedirs(os.path.dirname(self.full_build_path))
            except OSError:
                pass
            shutil.copy(self._preprocessing_path, self.full_build_path)

            self.site.plugin_manager.postBuildStatic(self)

    def __repr__(self):
        return '<Static: {0}>'.format(self.src_filename)