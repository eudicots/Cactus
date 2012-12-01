import os
import logging
import json
import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.settimeout(5)

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


