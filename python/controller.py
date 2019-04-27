from abc import ABC, abstractmethod


class ControllerInstance(ABC):
    @abstractmethod
    def process(self, angle):
        """
        This method takes a steering angle and passes it to a controller device.
        :param angle: Steering angle
        """