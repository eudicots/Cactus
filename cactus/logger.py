import os
import logging
import types
import json

import six


class JsonFormatter(logging.Formatter):

    def format(self, record):

        data = {}

        data["level"] = record.levelno
        data["levelName"] = record.levelname
        data["msg"] = logging.Formatter.format(self, record)
        # data["location"] = "%s/%s:%s" % (record.pathname, record.filename, record.lineno)

        if isinstance(record.args, types.DictType):
            for k, v in six.iteritems(record.args):
                data[k] = v

        return json.dumps(data)


def setup_logging():

    logger = logging.getLogger()
    handler = logging.StreamHandler()

    if os.environ.get('DESKTOPAPP'):
        log_level = logging.INFO

        handler.setFormatter(JsonFormatter())

    else:
        from colorlog import ColoredFormatter

        log_level = logging.INFO

        formatter = ColoredFormatter(
            "%(log_color)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'white',
                'INFO': 'white',
                'WARNING': 'bold_yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'bold_red',
            }
        )

        handler.setFormatter(formatter)

    logger.setLevel(log_level)

    logger.handlers = []
    logger.addHandler(handler)
