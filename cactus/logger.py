import os
import logging
import types
import json

import six


class JsonFormatter(logging.Formatter):

    def format(self, record):

        data = {
            "level": record.levelno,
            "levelName": record.levelname,
            "msg": logging.Formatter.format(self, record)
        }

        if type(record.args) is types.DictType:
            for k, v in six.iteritems(record.args):
                data[k] = v

        return json.dumps(data)


def setup_logging(verbose, quiet):

    logger = logging.getLogger()
    handler = logging.StreamHandler()

    if os.environ.get('DESKTOPAPP'):
        log_level = logging.INFO
        handler.setFormatter(JsonFormatter())

    else:
        from colorlog import ColoredFormatter

        formatter = ColoredFormatter(
                "%(log_color)s%(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                    'DEBUG':    'white',
                    'INFO':     'white',
                    'WARNING':  'bold_yellow',
                    'ERROR':    'bold_red',
                    'CRITICAL': 'bold_red',
                    }
                )

        if quiet:
            log_level = logging.WARNING
        elif verbose:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        handler.setFormatter(formatter)

    logger.setLevel(log_level)

    for h in logger.handlers:
        logger.removeHandler(h)

    logger.addHandler(handler)
