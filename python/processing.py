from abc import ABC, abstractmethod


class PreProcessingUnit(ABC):
    @abstractmethod
    def process(self, frame):
        """
        This method is doing something with your frame (e.g. resizing) and returns the new frame.
        :param frame: A frame you want to pre-process.
        :return: pre-processed frame.
        """


class ProcessingUnit(ABC):
    @abstractmethod
    def process(self, frame):
        """
        This method takes a frame and figures out the steering angle.
        :param frame: A frame you want to process.
        :return: Steering angle.
        """