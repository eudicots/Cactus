import os
import sys
import subprocess
import shutil

from distutils.sysconfig import get_python_lib
from setuptools import setup


VERSION = "3.3.3"
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

# From Django

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


EXCLUDE_FROM_PACKAGES = ['cactus.skeleton',]

def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
cactus_dir = 'cactus'

for dirpath, dirnames, filenames in os.walk(cactus_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])


def find_requirements():
    # Find all requirements.VERSION.txt files that match (e.g. Python 2.6 matches
    # requirements.2.6.txt, requirements.2.txt, and requirments.txt).
    v = [str(x) for x in  sys.version_info[:2]]
    requirements = []
    while True:
        reqs_file = '.'.join(["requirements"] + v + ["txt"])
        try:
            with open(os.path.join(root_dir, reqs_file)) as f:
                requirements.extend(f.readlines())
        except IOError:
            pass
        try:
            v.pop()
        except IndexError:
            break

    return requirements

setup(
    name='Cactus',
    version=VERSION,
    description="Static site generation and deployment.",
    long_description=open('README.md').read(),
    url='http://github.com/koenbok/Cactus',
    author='Koen Bok',
    author_email='koen@madebysofa.com',
    license='BSD',
    packages=packages,
    package_data=package_data,
    entry_points={
        'console_scripts': [
            'cactus = cactus.cli:cli_entrypoint',
        ],
    },
    install_requires=find_requirements(),
    extras_require={
        'GCS Deployment': ['google-api-python-client'],
        'Cloud Files Deployment': ['pyrax'],
        'Mac Native FSEvents': ['macfsevents'],
    },
    tests_require=open(os.path.join(root_dir, "test_requirements.txt")).readlines(),
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
