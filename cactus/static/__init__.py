#coding:utf-8
import os
import logging
import tempfile
import shutil

from cactus.compat.paths import StaticCompatibilityLayer
from cactus.utils.file import calculate_file_checksum, file_changed_hash
from cactus.utils.filesystem import alt_file, mkdtemp
from cactus.utils.url import ResourceURLHelperMixin


logger = logging.getLogger(__name__)

class Static(StaticCompatibilityLayer, ResourceURLHelperMixin):
    """
    A static resource in the repo
    """

    discarded = False

    def __init__(self, site, path, relative_to=None):
        """
        :param site: The site that's building this static file
        :param path: The location where this static file is to be found
        :param relative_to: Location this path is relative to. Optional, and defaults to the site's path.
        """
        self.site = site
        self.path = path
        self.relative_to = relative_to

        _static_path, filename = os.path.split(path)

        # Actual source file
        self.src_dir = os.path.join('static', _static_path)
        self.src_filename = filename

        try:
            self.src_name, self.src_extension = filename.rsplit('.', 1)
        except ValueError:
            self.src_name = filename
            self.src_extension = ""

        # Useless, we'll crash before.
        # # TODO
        # assert self.src_extension, "No extension for file?! {0}".format(self.src_name)

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

        if not hasattr(self.site, "_static_file_cache"):
            self.site._static_file_cache = {}


    @property
    def full_source_path(self):
        if self.relative_to is not None:
            relative_to = self.relative_to
        else:
            relative_to = self.site.path

        full_source_path = os.path.join(relative_to, self.src_dir, self.src_filename)

        if os.path.islink(full_source_path):
            return os.path.realpath(full_source_path)

        return full_source_path

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
    def _final_url(self):
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
        self.pre_dir = mkdtemp()
        pre_path = os.path.join(self.pre_dir, self.src_filename)

        shutil.copy(self.full_source_path, pre_path)

        # Pre-process
        logger.debug('Pre-processing: %s %s', self.src_name, self.pre_dir)

        # Run processors (those might change the extension)
        self.final_extension = self.run_externals(self.src_extension, pre_path, self.site.external_manager.processors)

        # Optimize
        if not self.discarded:
            # Run optimizes and make sure they don't alter the extension
            _ = self.run_externals(self.final_extension, pre_path, self.site.external_manager.optimizers)
            assert self.final_extension == _, "Illegal Optimizer: may not change the extension"
            assert not self.discarded, "Illegal Optimizer: may not discard files"

        return pre_path

    def discard(self):
        self.discarded = True  #TODO: Warn on usage of the static!

    def build(self):

        # See if we can maybe skip this if the file did not change
        curr_hash = file_changed_hash(self.full_source_path)
        prev_hash = self.site._static_file_cache.get(self.full_source_path)

        if os.path.exists(self.full_build_path):
            if curr_hash == prev_hash:
                logger.debug("skip building (unchanged) %s %s", self.src_name, self.final_url)
                return

        self.site._static_file_cache[self.full_source_path] = curr_hash

        self.site.plugin_manager.preBuildStatic(self)

        if self.discarded:
            return

        logger.debug('Building {0} --> {1}'.format(self.src_name, self.full_build_path))

        try:
            os.makedirs(os.path.dirname(self.full_build_path))
        except OSError:
            pass

        shutil.copy(self._preprocessing_path, self.full_build_path)

        # self.site.plugin_manager.postBuildStatic(self)

    def __repr__(self):
        return '<Static: {0}>'.format(self.src_filename)
