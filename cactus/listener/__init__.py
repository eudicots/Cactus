from cactus.listener.polling import PollingListener

Listener = PollingListener

try:
    from mac import FSEventsListener
    Listener = FSEventsListener
except ImportError:
    pass
