import os
import logging
import types
import json

class JsonFormatter(logging.Formatter):

    def format(self, record):

        data = {}

        data["level"] = record.levelno
        data["levelName"] = record.levelname
        data["msg"] = logging.Formatter.format(self, record)
        # data["location"] = "%s/%s:%s" % (record.pathname, record.filename, record.lineno)

        if type(record.args) is types.DictType:
            for k, v in record.args.iteritems():
                data[k] = v

        return json.dumps(data)


def setup_logging():

    logger = logging.getLogger()
    handler = logging.StreamHandler()

    if os.environ.get('DEBUG'):
        log_level = logging.DEBUG
        log_format = '%(name)s:%(lineno)s / %(levelname)s -> %(message)s'

        handler.setFormatter(logging.Formatter(fmt=log_format))

    elif os.environ.get('DESKTOPAPP'):
        log_level = logging.INFO
        log_format = '%(message)s'

        handler.setFormatter(JsonFormatter())

    else:
        log_level = logging.INFO
        log_format = '%(message)s'

        handler.setFormatter(logging.Formatter(fmt=log_format))

    logger.setLevel(log_level)

    logger.handlers = []
    logger.addHandler(handler)
    