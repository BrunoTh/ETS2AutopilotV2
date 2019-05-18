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
    @staticmethod
    @abstractmethod
    def get_html_source(settings_node) -> str:
        """
        This method returns html code of the widget.
        :type settings_node: SettingsNode
        """


class TextWidget(HTMLWidget):
    """
    Renders text input.
    """
    @staticmethod
    def get_html_source(settings_node) -> str:
        return f'<input type="text" id="id_{settings_node.key}" value="{settings_node.value}" />'


class SelectWidget(HTMLWidget):
    """
    Renders select tag.
    """
    @staticmethod
    def get_html_source(settings_node) -> str:
        html = f'<select id="id_{settings_node.key}">\n'

        for child in settings_node.children:
            if child.is_choice and child.widget:
                html += child.render_element()
                html += '\n'

        html += f'</select>'
        return html


class OptionWidget(HTMLWidget):
    """
    Renders option tag.
    """
    @staticmethod
    def get_html_source(settings_node) -> str:
        return f'<option id="id_{settings_node.key}">{settings_node.key}</option>'


class SettingsNode:
    ROOT_NODE_NAME = 'root'

    def __init__(self, key='', value='', is_choice=False, widget=None):
        self.fqid = SettingsNode.ROOT_NODE_NAME  # fully qualified id (e.g. root.controller.device_id)
        self.children = []
        self.possible_choices = []
        self.is_root = False
        self.is_choice = is_choice
        self.widget = widget

        self.key = key
        self.value = value

    def __str__(self):
        return self.fqid

    def _set_fqid(self, parent_node):
        """
        Generates the fqid for every child recursively.
        :param parent_node:
        :type parent_node: SettingsNode
        """
        self.fqid = f'{parent_node.fqid}.{self.key}'

        for child in self.children:
            child._set_fqid(self)

    def add_child(self, child):
        """

        :param child: SettingsNode you want to add as child.
        :type child: SettingsNode
        :return:
        """
        if not isinstance(child, SettingsNode):
            raise TypeError(f'Object of type {type(child)} is not supported.')

        child._set_fqid(self)
        self.children.append(child)

        if self.is_choice:
            self.possible_choices.append(child)

    # def choose(self, children):
    #     self.children = children.copy()

    def set_value_of_child(self, child_path: str, value):
        """
        Gets the child behind child_path and sets its value to the given value.
        :param child_path: Path relative to this parent node.
        :param value: Value you want to set.
        """
        self.get_node_in_tree(child_path).value = value

    def get_value_of_child(self, child_path: str):
        """
        Gets the child behind child_path and returns its value.
        :param child_path: Path relative to this parent node.
        :return: Value of child.
        """
        return self.get_node_in_tree(child_path).value

    def get_node_in_tree(self, child_path: str):
        """
        Returns the child object behind child_path.
        :param child_path: Path relative to this parent node.
        :return: children behind child_path
        :rtype: SettingsNode
        """
        if child_path.startswith(f'{SettingsNode.ROOT_NODE_NAME}.'):
            child_path = child_path.replace(f'{SettingsNode.ROOT_NODE_NAME}.', '')

        next_path_elements = child_path.split('.', maxsplit=1)
        for child in self.children:
            if child.key == next_path_elements[0]:
                if len(next_path_elements) == 1:
                    return child
                else:
                    return child.get_node_in_tree(next_path_elements[1])

    def get_sub_tree(self):
        """
        This method is used to generate a dict structure of this settings tree.
        It returns either a dict if this node still has children or just self.value.
        """
        if not self.children:
            return self.value

        result = dict()
        result['fqid'] = self.fqid

        for child in self.children:
            if child.is_choice:
                result['value'] = child.key
                result.update(child.get_sub_tree())
            else:
                result[child.key] = child.get_sub_tree()
        return result

    def render_element(self) -> str:
        """
        If self.widget is set it returns the generated html code for this SettingsNode.
        :return: HTML Code
        """
        if not self.widget:
            raise ValueError('A widget is required to render this element.')

        return self.widget().get_html_source(self)


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
