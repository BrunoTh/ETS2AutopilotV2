from logging import Logger
from abc import ABC, abstractmethod
from .builtin import ChainElement, ProcessingResult
import numpy as np

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

    def import_dependencies(self):
        # TODO: make this work... please.
        from PIL import ImageGrab as ImageGrabWindows

    def process(self, *args, **kwargs):
        # TODO: bbox (Via settings?)
        frame_screen = ImageGrabWindows.grab()
        frame_screen_converted = np.uint8(frame_screen)
        return ProcessingResult(args=(frame_screen_converted,))


class PyscreenshotDevice(CapturingDevice):
    """
    Pyscreenshot CapturingDevice.
    Usable on Linux.
    """
    def import_dependencies(self):
        import pyscreenshot as ImageGrabLinux

    def process(self, *args, **kwargs):
        # TODO: bbox (Via settings?)
        frame_screen = ImageGrabLinux.grab()
        frame_screen_converted = np.uint8(frame_screen)
        return ProcessingResult(args=(frame_screen_converted,))
