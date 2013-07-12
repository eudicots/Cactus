class ExternalManager(object):
    """
    Manager the active externals
    """
    def __init__(self, site, processors=None, optimizers=None):
        self.site = site
        self.processors = processors if processors is not None else []
        self.optimizers = optimizers if optimizers is not None else []

    def _register(self, external, externals):
        externals.insert(0, external)

    def _deregister(self, external, externals):
        externals.remove(external)

    def clear(self):
        """
        Clear this manager
        """
        self.processors = []
        self.optimizers = []

    def register_processor(self, processor):
        """
        Add a new processor to the list of processors
        This processor will be added with maximum priority
        """
        self._register(processor, self.processors)

    def deregister_processor(self, processor):
        """
        Remove an existing processor from the list
        Will raise a ValueError if the processor is not present
        """
        self._deregister(processor, self.processors)

    def register_optimizer(self, optimizer):
        """
        Add a new optimizer to the list of optimizer
        This optimizer will be added with maximum priority
        """
        self._register(optimizer, self.optimizers)

    def deregister_optimizer(self, processor):
        """
        Remove an existing optimizer from the list
        Will raise a ValueError if the optimizer is not present
        """
        self._deregister(processor, self.optimizers)
