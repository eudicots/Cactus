#coding:utf-8
import logging


class ExternalFailure(Exception):
    """
    Raised when an External failed to run
    """
    def __init__(self, external, error):
        self.external = external
        self.error = error

    def __str__(self):
        return '{0} failed: {1}'.format(self.external, self.error)


class ExternalProcessor(object):
    supported_extensions = ()  # The extensions supported by this output
    output_extension = 'css'  # The extension of this processor's output
    critical = False  # Whether this External failure is critical

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def run(self):
        """
        Return True in the case we succeed in running, False otherwise.
        This means we can use several processors and have one or the other work.
        """
        logging.info('Running external: {0}'.format(self.__class__.__name__))
        try:
            self._run()

        except OSError, e:
            msg = 'Could not call external processor {0}: {1}'.format(self.__class__.__name__, e)

            if self.critical:
                logging.critical(msg)
                raise ExternalFailure(self.__class__.__name__, e)
            else:
                logging.info(msg)
                return False

        return True

    def _run(self):
        raise NotImplementedError()