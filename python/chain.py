from abc import ABC, abstractmethod
from . import capturing
from . import processing
from . import controller


class ProcessingChain(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def run(self):
        pass


class AP1ChainWindows(ProcessingChain):
    def __init__(self):
        super().__init__()

    def run(self):
        pass
