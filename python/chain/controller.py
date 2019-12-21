from logging import Logger
from abc import ABC, abstractmethod
from .builtin import ChainElement, ProcessingResult
from settingstree import SettingsNode, NodeInput

log = Logger(__name__)


class ControllerInstance(ChainElement):
    @abstractmethod
    def process(self, angle, *args, **kwargs):
        """
        This method takes a steering angle and passes it to a controller device.
        :param angle: Steering angle (-1 <= angle <= 1)
        """


class VjoyController(ControllerInstance):
    """
    ControllerInstance for VJoy.
    """
    def __init__(self):
        super().__init__()

        self.vjoy_device = SettingsNode(key='vjoy_device', value='0', widget=NodeInput, verbose_name='vJoy Device ID')

    def import_dependencies(self):
        self._import_helper('pyvjoy', 'pyvjoy')

    def process(self, angle, *args, **kwargs):
        # Write angle to vjoy.
        vjoy_controller = self._imported_dependencies['pyvjoy'].VJoyDevice(int(self.vjoy_device.value))
        vjoy_controller.reset()

        vjoy_angle = (angle + 1) * 32768 / 2

        vjoy_controller.set_axis(self._imported_dependencies['pyvjoy'].HID_USAGE_X, vjoy_angle)

        # Send angle to UI
        return ProcessingResult(data_to_send={'angle': angle})
