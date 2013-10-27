import os
import logging
import json
import types


class JsonFormatter(logging.Formatter):

    def format(self, record):

        data = {}

    	data["level"] = record.levelno
        data["levelName"] = record.levelname
       	data["msg"] = logging.Formatter.format(self, record)

    	if type(record.args) is types.DictType:
        	for k, v in record.args.iteritems():
        		data[k] = v

        return json.dumps(data)

class SignalLogger(logging.Logger):
    def signal(self, name, data={}):
    	data["signal"] = name
    	self.debug("", data)

logging.setLoggerClass(SignalLogger)

def setup_logging():
    if os.environ.get('DEBUG'):
        logging.basicConfig(
            format = '%(name)s:%(lineno)s / %(levelname)s -> %(message)s',
            level = logging.DEBUG
        )
    elif os.environ.get('DESKTOPAPP'):
	    logging.basicConfig(
	        format = '%(message)s',
	        level = logging.INFO,
	    )
	   	
	    handler = logging.getLogger().handlers[0]
	    handler.setFormatter(JsonFormatter())

    else:
        logging.basicConfig(
            format = '%(message)s',
            level = logging.INFO
        )