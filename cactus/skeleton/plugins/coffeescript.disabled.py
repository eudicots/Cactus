import os
import pipes
import subprocess
import logging

def run(command):

    logger = logging.getLogger(__name__)

    logger.debug(command)

    os.environ['PATH'] = '/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/share/npm/bin:'

    process = subprocess.Popen([command],
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout = process.stdout.readline()
    stderr = process.stderr.readline()

    if stdout: logger.info(stdout)
    if stderr: logger.warning(stderr)


def preBuild(site):
    run('coffee -c %s/js/*.coffee' % pipes.quote(site.static_path))
