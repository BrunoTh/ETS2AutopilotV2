from logging import Logger
from abc import ABC, abstractmethod
from .builtin import ChainElement, ProcessingResult

log = Logger(__name__)


class CapturingDevice(ChainElement):
    @abstractmethod
    def process(self, *args, **kwargs):
        """
        This method returns the current frame from the capturing device.
        """


class ImageGrabDevice(CapturingDevice):
    """
    ImageGrab CapturingDevice.
    Usable on Windows.
    """

    def process(self, *args, **kwargs):
        return ProcessingResult()


class PyscreenshotDevice(CapturingDevice):
    """
    Pyscreenshot CapturingDevice.
    Usable on Linux.
    """
    def process(self, *args, **kwargs):
        return ProcessingResult()
