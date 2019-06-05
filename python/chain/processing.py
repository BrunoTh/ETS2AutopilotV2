from logging import Logger
from abc import ABC, abstractmethod
from . import ChainElement
from api import WebSocketMixin
from settingstree import SettingsNode

log = Logger(__name__)


class PreProcessingUnit(ChainElement):
    @abstractmethod
    def process(self, frame):
        """
        This method is doing something with your frame (e.g. resizing) and returns the new frame.
        :param frame: A frame you want to pre-process.
        :return: pre-processed frame.
        """


class ProcessingUnit(ChainElement):
    @abstractmethod
    def process(self, frame):
        """
        This method takes a frame and figures out the steering angle.
        :param frame: A frame you want to process.
        :return: Steering angle.
        """


class ColorConversionPreProcessingUnit(PreProcessingUnit):
    def process(self, frame):
        return frame


class ROIPreProcessingUnit(PreProcessingUnit):
    VERBOSE_NAME = 'Viewport'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.x1 = SettingsNode(key='x1')
        self.x2 = SettingsNode(key='x2')
        self.y1 = SettingsNode(key='y1')
        self.y2 = SettingsNode(key='y2')

    def process(self, frame):
        return frame


class CVLaneDetectionProcessingUnit(ProcessingUnit, WebSocketMixin):
    def process(self, frame):
        angle = 0
        # TODO: Also send image with drawn lanes to webapp.
        self.send_via_websocket(angle)
        return angle
