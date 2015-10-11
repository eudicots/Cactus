import logging


from cactus.listener.polling import PollingListener


logger = logging.getLogger(__name__)


try:
    from cactus.listener.mac import FSEventsListener as Listener
except (ImportError, OSError):
    logger.debug("Failed to load FSEventsListener, falling back to PollingListener", exc_info=True)
    Listener = PollingListener
