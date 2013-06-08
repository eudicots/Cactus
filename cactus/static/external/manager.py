class ExternalManager(object):
    """
    Manager the active externals
    """
    def __init__(self, processors=None, optimizers=None):
        self.processors = processors if processors is not None else []
        self.optimizers = optimizers if optimizers is not None else []

    def _register(self, external, externals):
        externals.insert(0, external)

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

    def register_optimizer(self, optimizer):
        """
        Add a new optimizer to the list of optimizer
        This optimizer will be added with maximum priority
        """
        self._register(optimizer, self.optimizers)