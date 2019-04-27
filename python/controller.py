from logging import Logger
from abc import ABC, abstractmethod
from .chain import ChainElement

log = Logger(__name__)


class ControllerInstance(ChainElement):
    @abstractmethod
    def process(self, angle):
        """
        This method takes a steering angle and passes it to a controller device.
        :param angle: Steering angle
        """


class VjoyController(ControllerInstance):
    """
    ControllerInstance for VJoy.
    """
    def __init__(self, vjoy_device: int):
        super().__init__()
        self.vjoy_device = vjoy_device

    def process(self, angle):
        # Write angle to vjoy.
        pass
