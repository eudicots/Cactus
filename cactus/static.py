#coding:utf-8
import os
import logging
import subprocess
import tempfile
import shutil
import hashlib
from contextlib import contextmanager


CONVERSIONS = {"sass": "css", "scss": "css"}


def calculate_file_checksum(path):
    """
    Calculate the MD5 sum for a file (needs to fit in memory)
    """
    with open(path) as f:
        return hashlib.md5(f.read()).hexdigest()


class Static(object):
    """
    A static resource in the repo
    """

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

        # Where the file should be referenced in source files
        self.final_extension = CONVERSIONS.get(self.src_extension, self.src_extension)

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

        # Path where the file should be built to.
        self.build_path = os.path.join(self.src_dir, self.final_name)
        # Path where the file should be referenced in built files
        self.final_url = "/{0}".format(self.build_path)

        self.paths = {
            'full': self._preprocessing_path,
            'full-build': os.path.join(site.paths['build'], self.build_path),
        }

    def pre_process(self):
        """
        Does file pre-processing if required
        """
        self.pre_dir = tempfile.mkdtemp()
        pre_path = os.path.join(self.pre_dir, 'file')

        shutil.copy(os.path.join(self.site.path, self.src_dir, self.src_filename), pre_path)

        # Pre-process
        logging.info('Pre-processing: %s' % self.src_name)

        @contextmanager
        def alt_file(current_file):
            _alt_file = current_file + '-alt'
            yield _alt_file
            try:
                shutil.move(_alt_file, current_file)
            except IOError:
                # We didn't use an alt file.
                pass

        with alt_file(pre_path) as tmp_file:
            try:
                if self.src_extension == 'sass':
                    logging.info('Processing (sass) {0}'.format(self))
                    subprocess.call(['sass', pre_path, tmp_file])
                if self.src_extension == 'scss':
                    logging.info('Processing (scss) {0}'.format(self))
                    subprocess.call(['sass', '--scss', pre_path, tmp_file])
            except OSError:
                raise Exception('SASS file found, but sass not installed.')

        # Optimize

        with alt_file(pre_path) as tmp_file:

            if self.site.optimize:
                try:
                    if self.final_extension == 'js':
                        logging.info('Compiling (closure) {0}'.format(self))
                        subprocess.call([
                            'closure-compiler',
                            '--js', pre_path,
                            '--js_output_file', tmp_file,
                            '--compilation_level', 'SIMPLE_OPTIMIZATIONS'
                        ])

                    elif self.final_extension == 'css':
                        logging.info('Minifying (yui) {0}'.format(self))
                        subprocess.call([
                            'yuicompressor',
                            '--type', 'css',
                            '-o', tmp_file,
                            pre_path,
                        ])

                except OSError:
                    logging.warning('Aborted optimization: missing external.')

        return pre_path

    def build(self):
        logging.info('Building {0} --> {1}'.format(self.src_name, self.final_url))

        try:
            os.makedirs(os.path.dirname(self.paths['full-build']))
        except OSError:
            pass

        copy = lambda: shutil.copy(self.paths['full'], self.paths['full-build'])

        copy()

    def __repr__(self):
        return '<Static: {0}>'.format(self.src_filename)
