from abc import ABC, abstractmethod


class CapturingDevice(ABC):
    @abstractmethod
    def get_frame(self):
        """
        This method returns the current frame from the capturing device.
        """