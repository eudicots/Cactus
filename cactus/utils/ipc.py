import logging

def signal(signal, data={}):
	data["signal"] = signal
	logging.warning("", data)