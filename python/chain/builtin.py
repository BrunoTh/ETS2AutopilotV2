from abc import ABC, abstractmethod
from settingstree import SettingsNode
from settingstree.widgets.nodewidgets import NodeSubtree
from collections import namedtuple
from importlib import import_module

ProcessingResult = namedtuple('ProcessingResult', ('args', 'kwargs', 'data_to_send'), defaults=([], {}, {}))


class ChainElement(ABC):
    VERBOSE_NAME = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._imported_dependencies = dict()
        self.import_dependencies()

    def collect_settings(self) -> SettingsNode:
        """
        This methods searches for instances of SettingsNodes, adds them as children to a parent SettingsNode and
        returns it.
        :return: SettingsNode object with found children attached.
        """
        settings_node = SettingsNode(key=self.__class__.__name__, verbose_name=self.__class__.VERBOSE_NAME,
                                     widget=NodeSubtree)
        for attribute in dir(self):
            if isinstance(getattr(self, attribute), SettingsNode):
                settings_node.add_child(getattr(self, attribute))

        return settings_node

    def _import_helper(self, module: str, alias: str):
        """
        Uses importlib.import_module to import the given module and adds it to the dict self._imported_dependencies with
        alias as key.
        :param module: Modulename (e.g. pathlib.Path)
        :param alias: Alias for module (e.g. Path or pathlib_path)
        """
        self._imported_dependencies[alias] = import_module(module)

    def import_dependencies(self):
        """
        Import python libs here. Gets called on init.
        """
        pass

    @abstractmethod
    def process(self, *args, **kwargs) -> ProcessingResult:
        """

        :param args:
        :return:
        """

