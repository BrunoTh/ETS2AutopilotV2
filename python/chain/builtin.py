from abc import ABC, abstractmethod
from settingstree import SettingsNode
from settingstree.widgets import SubtreeWidget


class ChainElement(ABC):
    VERBOSE_NAME = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def collect_settings(self) -> SettingsNode:
        """
        This methods searches for instances of SettingsNodes and adds them to self._settings_node.
        :return: self._settings_node
        """
        settings_node = SettingsNode(key=self.__class__.__name__, verbose_name=self.__class__.VERBOSE_NAME,
                                     widget=SubtreeWidget)
        for attribute in dir(self):
            if attribute != '_settings_node' and isinstance(getattr(self, attribute), SettingsNode):
                settings_node.add_child(getattr(self, attribute))

        return settings_node

    @abstractmethod
    def process(self, *args):
        """

        :param args:
        :return:
        """

