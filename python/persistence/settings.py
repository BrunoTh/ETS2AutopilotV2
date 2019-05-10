from logging import Logger
from abc import ABC, abstractmethod
import json
import pathlib

log = Logger(__name__)
# Path object of python/ directory.
BASE_PATH = pathlib.Path(__file__).parent
DEFAULT_NAME = 'settings.json'


"""
Settings structure
==================
root
  input_device = 
    * keyboard
      autopilot_button
    * gamepad
      device_id
      autopilot_button
      steering_axis
    * wheel
      device_id
      autopilot_button
      steering_axis
  viewport
    x1
    x2
    y1
    y2
  
"""


class HTMLWidget(ABC):
    def __init__(self, settings_node):
        self.settings_node = settings_node

    @abstractmethod
    def get_html_source(self) -> str:
        """
        This method returns html code of the widget.
        """


class SelectWidget(HTMLWidget):
    def get_html_source(self):
        return f'<input type="text" id="id_{self.settings_node.key}" value="{self.settings_node.value}" />'


class SettingsNode:
    possible_choices = []

    def __init__(self, key='', value='', is_choice=False, widget=None):
        self.children = []
        self.is_root = False
        self.is_choice = is_choice
        self.widget = widget

        self.key = key
        self.value = value

    def add_child(self, child):
        if not isinstance(child, SettingsNode):
            raise TypeError(f'Object of type {type(child)} is not supported.')
        self.children.append(child)

    def choose(self, children):
        self.children = children.copy()

    def set_value_of_child(self, child_path: str, value):
        self.get_child_in_tree(child_path).value = value

    def get_value_of_child(self, child_path: str):
        return self.get_child_in_tree(child_path).value

    def get_child_in_tree(self, child_path: str):
        next_path_elements = child_path.split('.', maxsplit=1)
        if len(next_path_elements) == 1:
            return self
        else:
            for child in self.children:
                if child.key == next_path_elements[0]:
                    return child.get_value_of_child(next_path_elements[1])

    def get_sub_tree(self):
        """
        This method is used to generate a dict structure of this settings tree.
        It returns either a dict if this node still has children or just self.value.
        """
        if not self.children:
            return self.value

        result = dict()
        for child in self.children:
            if child.is_choice:
                result['value'] = child.key
                result.update(child.get_sub_tree())
            else:
                result[child.key] = child.get_sub_tree()
        return result

    def render_element(self):
        if self.widget:
            return self.widget(self).get_html_source()


# TODO: singleton?
class Settings:
    INPUT_DEVICE_TYPE = 'controller_type'
    INPUT_DEVICE_TYPE_KEYBOARD = 0
    INPUT_DEVICE_TYPE_GAMEPAD = 1
    INPUT_DEVICE_TYPE_WHEEL = 2

    INPUT_DEVICE_AXIS_STEERING = ''
    VIRTUAL_CONTROLLER_ID = 'controller_id'  # id of the controller (e.g. vjoy device id)
    VIEWPORT_ROI_X1 = 'viewport_roi_x1'
    VIEWPORT_ROI_X2 = 'viewport_roi_x2'
    VIEWPORT_ROI_Y1 = 'viewport_roi_y1'
    VIEWPORT_ROI_Y2 = 'viewport_roi_y2'

    def __init__(self, filename=DEFAULT_NAME):
        self.filename = filename
        self._file_object = None
        self._parsed_json = dict()

        try:
            with open(self.filename) as f:
                self._parsed_json = json.load(self._file_object)
        except Exception:
            log.exception(f'Error while opening {self.filename}.')

    def get_file_object(self):
        if not self._file_object:
            self._file_object = open(self.filename, 'r')

        return self._file_object

    def close_file_object(self):
        if self._file_object:
            try:
                self._file_object.close()
                self._file_object = None
            except Exception:
                log.exception('Error while closing Settings.file_object.')

    def parse_json(self, force=False):
        if self._parsed_json and not force:
            return

        self._parsed_json = json.load(self.get_file_object())
        self.close_file_object()

    def dump_json(self):
        json.dump(self._parsed_json, self.get_file_object())
        self.close_file_object()

    def get_value(self, key):
        self.parse_json()
        # TODO: Pass KeyError or wrap error with own SettingsKeyError Exception?
        return self._parsed_json[key]

    def write_value(self, key, value):
        self.parse_json()
        self._parsed_json[key] = value
        self.dump_json()

    def delete_key(self, key):
        self.parse_json()
        # TODO: Pass KeyError or wrap error with own SettingsKeyError Exception?
        self._parsed_json.pop(key)
        self.dump_json()
