from logging import Logger
from abc import ABC, abstractmethod
from .builtin import ChainElement, ProcessingResult
from settingstree import SettingsNode, TextWidget

log = Logger(__name__)


class PreProcessingUnit(ChainElement):
    @abstractmethod
    def process(self, frame, *args, **kwargs):
        """
        This method is doing something with your frame (e.g. resizing) and returns the new frame.
        :param frame: A frame you want to pre-process.
        :return: pre-processed frame.
        """


class ProcessingUnit(ChainElement):
    @abstractmethod
    def process(self, frame, *args, **kwargs):
        """
        This method takes a frame and figures out the steering angle.
        :param frame: A frame you want to process.
        :return: Steering angle.
        """


class ColorConversionPreProcessingUnit(PreProcessingUnit):
    def process(self, frame, *args, **kwargs):
        return ProcessingResult()


class ROIPreProcessingUnit(PreProcessingUnit):
    VERBOSE_NAME = 'Viewport'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.x1 = SettingsNode(key='x1', widget=TextWidget)
        self.x2 = SettingsNode(key='x2', widget=TextWidget)
        self.y1 = SettingsNode(key='y1', widget=TextWidget)
        self.y2 = SettingsNode(key='y2', widget=TextWidget)

    def process(self, frame, *args, **kwargs):
        return ProcessingResult()


class CVLaneDetectionProcessingUnit(ProcessingUnit):
    def process(self, frame, *args, **kwargs):
        angle = 0
        # TODO: Also send image with drawn lanes to webapp.
        return ProcessingResult()
