from logging import Logger
from abc import ABC, abstractmethod
from .chain import ChainElement
from .api import WebSocketMixin

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
    def process(self, frame):
        return frame


class CVLaneDetectionProcessingUnit(ProcessingUnit, WebSocketMixin):
    def process(self, frame):
        angle = 0
        # TODO: Also send image with drawn lanes to webapp.
        self.send_via_websocket(angle)
        return angle
