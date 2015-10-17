import os
import logging


def signal(signal, data=None):
    if data is None:
        data = {}

    if not os.environ.get('DESKTOPAPP'):
        return

    data["signal"] = signal
    logging.warning("", data)
