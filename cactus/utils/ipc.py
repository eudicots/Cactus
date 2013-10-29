import os
import logging

def signal(signal, data={}):
	
	if not os.environ.get('DESKTOPAPP'):
		return
		
	data["signal"] = signal
	logging.warning("", data)