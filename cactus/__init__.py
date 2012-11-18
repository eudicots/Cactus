import os
import logging
import json
import socket

# I don't think this is actually working
socket.setdefaulttimeout(5.0)

logLevel = logging.INFO

if os.environ.get('DEBUG'):
	logging.basicConfig(
		format='%(filename)s:%(lineno)s / %(levelname)s -> %(message)s', 
		level=logging.DEBUG
	)
else:
	logging.basicConfig(
		format='%(message)s', 
		level=logging.INFO
	)

from site import Site


