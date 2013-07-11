import os
import sys
import subprocess
import shutil

from distutils.sysconfig import get_python_lib
from setuptools import setup


VERSION = "2.5.0"
SKELETON_FOLDERS = ['pages', 'plugins', 'static/css', 'static/images', 'static/js', 'templates', 'locale']
SKELETON_GLOB = ['skeleton/{0}/*'.format(folder) for folder in SKELETON_FOLDERS]

if "uninstall" in sys.argv:

    def run(command):
        try:
            return subprocess.check_output(command, shell = True).strip()
        except subprocess.CalledProcessError:
            pass

    cactusBinPath = run('which cactus')
    cactusPackagePath = None

    for p in os.listdir(get_python_lib()):
        if p.lower().startswith('cactus') and p.lower().endswith('.egg'):
            cactusPackagePath = os.path.join(get_python_lib(), p)

    if cactusBinPath and os.path.exists(cactusBinPath):
        sys.stdout.write('Removing cactus script at %s' % cactusBinPath)
        os.unlink(cactusBinPath)

    if cactusPackagePath and os.path.isdir(cactusPackagePath):
        sys.stdout.write('Removing cactus package at %s' % cactusPackagePath)
        shutil.rmtree(cactusPackagePath)

    sys.exit()

if "install" in sys.argv or "bdist_egg" in sys.argv:

    # Check if we have an old version of cactus installed
    p1 = '/usr/local/bin/cactus.py'
    p2 = '/usr/local/bin/cactus.pyc'

    if os.path.exists(p1) or os.path.exists(p2):
        sys.stdout.write("Error: you have an old version of Cactus installed, we need to move it:")
        if os.path.exists(p1):
            sys.stderr.write("  sudo rm %s" % p1)
        if os.path.exists(p2):
            sys.stderr.write("  sudo rm %s" % p2)
        sys.exit()

setup(
    name='Cactus',
    version=VERSION,
    description="Static site generation and deployment.",
    long_description=open('README.md').read(),
    url='http://github.com/koenbok/Cactus',
    download_url='https://github.com/koenbok/Cactus/tarball/v%s#egg=Cactus-%s' % (VERSION, VERSION),
    author='Koen Bok',
    author_email='koen@madebysofa.com',
    license='BSD',
    packages=[
        'cactus', 'cactus.utils', 'cactus.plugin', 'cactus.plugin.builtin',
        'cactus.static', 'cactus.static.external',
        'cactus.i18n', 'cactus.config',
        'cactus.contrib', 'cactus.contrib.external',
        'cactus.bootstrap', 'cactus.compat', 'cactus.credentials',
        'cactus.deployment', 'cactus.deployment.s3'
        ],
    package_data={'cactus': SKELETON_GLOB, },
    exclude_package_data={'cactus': SKELETON_FOLDERS},
    entry_points={
        'console_scripts': [
            'cactus = cactus.cli:main',
        ],
    },
    install_requires=[
        'Django',
        'boto>=2.4.1',
        'markdown',
        'argparse'
    ],
    zip_safe=False,
    setup_requires=['nose'],
    tests_require=['nose', 'mock', 'tox', 'unittest2'],
    classifiers=[],
)
