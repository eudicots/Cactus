import logging
from cactus.static.external.exceptions import ExternalFailure


logger = logging.getLogger(__name__)


# Helpers to build the Externals

ACCEPTED = 1
REFUSED = 0
DISCARDED = -1


def status_getter(status):
    def has_status(external):
        return external.status == status
    return has_status


def status_setter(status):
    def set_status(external):
        logger.debug('External {0} ({1}) status > {2}'.format(
            external.__class__.__name__, external.src, status))
        external.status = status
    return set_status


class External(object):
    supported_extensions = ()  # The extensions supported by this output
    output_extension = 'css'  # The extension of this processor's output
    critical = False  # Whether this External failure is critical

    def __init__(self, extension, src, dst):
        self.extension = extension
        self.src = src
        self.dst = dst

    accept = status_setter(ACCEPTED)
    accepted = status_getter(ACCEPTED)

    refuse = status_setter(REFUSED)
    refused = status_getter(REFUSED)

    discard = status_setter(DISCARDED)
    discarded = status_getter(DISCARDED)


    def run(self):
        """
        Return True in the case we succeed in running, False otherwise.
        This means we can use several processors and have one or the other work.
        """
        if not self.extension in self.supported_extensions:
            return self.refuse()

        self.accept()  # We accept now so the run method can discard

        try:
            self._run()
        except OSError as e:
            msg = 'Could not call external processor {0}: {1}'.format(self.__class__.__name__, e)

            if self.critical:
                logger.critical(msg)
                raise ExternalFailure(self.__class__.__name__, e)
            else:
                logger.info(msg)
                self.refuse()

    def _run(self):
        raise NotImplementedError()
