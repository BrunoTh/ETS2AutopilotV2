from logging import Logger
from abc import ABC, abstractmethod
from .builtin import ChainElement, ProcessingResult
from PIL import ImageGrab as ImageGrabWindows
import pyscreenshot as ImageGrabLinux

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
        # TODO: bbox (Via settings?)
        frame_screen = ImageGrabWindows.grab()
        return ProcessingResult(args=(frame_screen,))


class PyscreenshotDevice(CapturingDevice):
    """
    Pyscreenshot CapturingDevice.
    Usable on Linux.
    """
    def process(self, *args, **kwargs):
        # TODO: bbox (Via settings?)
        frame_screen = ImageGrabLinux.grab()
        return ProcessingResult(args=(frame_screen,))
