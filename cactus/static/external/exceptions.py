#coding:utf-8

class InvalidExternal(Exception):
    """
    Raised when an External caused an illegal operation.
    """
    #TODO: Tests


class ExternalFailure(Exception):
    """
    Raised when an External failed to run
    """
    def __init__(self, external, error):
        self.external = external
        self.error = error

    def __str__(self):
        return '{0} failed: {1}'.format(self.external, self.error)
