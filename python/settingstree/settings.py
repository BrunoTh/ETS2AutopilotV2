from logging import Logger
import json
from json.decoder import JSONDecodeError
import pathlib
from .widgets.nodewidgets import NodeSubtree


log = Logger(__name__)
# Path object of python/ directory.
BASE_PATH = pathlib.Path(__file__).parent
DEFAULT_NAME = 'settings.json'


class SettingsNode:
    ROOT_NODE_NAME = 'root'

    def __init__(self, key='', value='', is_choice=False, widget=None, verbose_name=None):
        self.fqid = SettingsNode.ROOT_NODE_NAME  # fully qualified id (e.g. root.controller.device_id)
        self.children = []
        self.possible_choices = []
        self.is_root = False
        self.is_choice = is_choice
        self.widget = widget
        self.verbose_name = verbose_name

        self.key = key
        self.value = value

    def __str__(self):
        return self.fqid

    @property
    def label(self):
        """
        Returns either verbose_name if set or key.
        """
        return self.verbose_name if self.verbose_name else self.key

    def _set_fqid(self, parent_node):
        """
        Generates the fqid for every child recursively.
        :param parent_node:
        :type parent_node: SettingsNode
        """
        self.fqid = f'{parent_node.fqid}.{self.key}'

        for child in self.children:
            child._set_fqid(self)

    def has_choices(self):
        return len(self.possible_choices) > 0

    def has_children(self):
        return len(self.children) > 0

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

        if child.is_choice:
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
        It returns either a dict if this node still has children. Otherwise just self.value.
        """
        if not self.children:
            return self.value

        result = dict()
        result['fqid'] = self.fqid

        for child in self.children:
            if self.has_choices():
                result['value'] = self.value
            result[child.key] = child.get_sub_tree()
        return result

    def get_flat_sub_tree(self) -> dict:
        """
        This method returns a dict with the child fqids as keys and child values as values. Like a key-value store.
        :return: key-value store
        """
        if not self.children:
            return {self.fqid: self.value}

        result = dict()

        for child in self.children:
            if self.has_choices():
                result.update({
                    f'{self.fqid}.value': self.value,
                })

            result.update(**child.get_flat_sub_tree())

        return result

    def fill_tree_flat(self, flat_values: dict):
        """
        This method writes previously exported values (with get_flat_sub_tree method) back to the settings tree.
        :param flat_values: previously exported dict
        """
        for fqid, value in flat_values.items():
            try:
                self.set_value_of_child(fqid, value)
            except:
                # fqid does not exist in tree.
                pass

    def render_element(self) -> str:
        """
        If self.widget is set it returns the generated html code for this SettingsNode.
        :return: HTML Code
        """
        if not self.widget:
            raise ValueError('A widget is required to render this element.')

        return self.widget(self).get_html_source()


# TODO: singleton?
class Settings:
    def __init__(self, filename=DEFAULT_NAME):
        self.filename = filename
        self._file_object = None
        self.root = SettingsNode(widget=NodeSubtree, verbose_name='Settings')

    def get_file_object(self):
        if not self._file_object:
            filepath = pathlib.Path() / self.filename
            if not filepath.exists():
                filepath.touch()

            self._file_object = open(filepath, 'r+')

        self._file_object.seek(0)

        return self._file_object

    def close_file_object(self):
        if self._file_object:
            try:
                self._file_object.close()
                self._file_object = None
            except Exception:
                log.exception('Error while closing Settings.file_object.')

    def dumps(self):
        return self.root.get_flat_sub_tree()

    def dump(self):
        f = self.get_file_object()
        try:
            current_settings = json.load(f) or dict()
        except json.decoder.JSONDecodeError:
            log.exception('Invalid json file.')
            current_settings = dict()

        # Delete file content.
        f.truncate(0)
        f.seek(0)
        tree_dict_flat = self.dumps()

        # Update the settings, leave old (currently unused values) untouched.
        current_settings.update(tree_dict_flat)
        json.dump(current_settings, f)
        f.flush()

    def load(self):
        f = self.get_file_object()
        try:
            json_dict = json.load(f)
            self.root.fill_tree_flat(json_dict)
        except JSONDecodeError:
            pass
