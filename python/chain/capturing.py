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
        self._import_helper('PIL.ImageGrab', 'ImageGrab')

    def process(self, *args, **kwargs):
        # TODO: bbox (Via settings?)
        frame_screen = self._imported_dependencies['ImageGrab'].grab()
        frame_screen_converted = np.uint8(frame_screen)
        return ProcessingResult(args=(frame_screen_converted,))


class PyscreenshotDevice(ImageGrabDevice):
    """
    Pyscreenshot CapturingDevice. Imports pyscreenshot as ImageGrab instead of PIL.ImageGrab.
    Usable on Linux.
    """
    def import_dependencies(self):
        self._import_helper('pyscreenshot', 'ImageGrab')
