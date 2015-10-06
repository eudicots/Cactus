import logging


from cactus.listener.polling import PollingListener


logger = logging.getLogger(__name__)


try:
    from cactus.listener.mac import FSEventsListener as Listener
except (ImportError, OSError):
    logger.warning("Failed to load FSEventsListener", exc_info=True)
    Listener = PollingListener
