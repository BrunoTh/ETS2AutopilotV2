from logging import Logger
from abc import ABC, abstractmethod
from . import ChainElement

log = Logger(__name__)


class CapturingDevice(ChainElement):
    @abstractmethod
    def process(self, *args):
        """
        This method returns the current frame from the capturing device.
        """


class ImageGrabDevice(CapturingDevice):
    """
    ImageGrab CapturingDevice.
    """

    def process(self, *args):
        pass
