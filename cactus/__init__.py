import os
import logging
import socket

from cactus.site import Site

socket.setdefaulttimeout(5)

if os.environ.get('DEBUG'):
    logging.basicConfig(
        format = '%(filename)s:%(lineno)s / %(levelname)s -> %(message)s',
        level = logging.DEBUG
    )
else:
    logging.basicConfig(
        format = '%(message)s',
        level = logging.INFO
    )