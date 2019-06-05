import platform
from abc import ABC, abstractmethod
from settingstree import Settings, SettingsNode


class ChainElement(ABC):
    VERBOSE_NAME = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def collect_settings(self) -> SettingsNode:
        """
        This methods searches for instances of SettingsNodes and adds them to self._settings_node.
        :return: self._settings_node
        """
        settings_node = SettingsNode(key=self.__class__.__name__, verbose_name=self.__class__.VERBOSE_NAME)
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


class ProcessingChain(ABC):
    # Use this chain if platform string matches platform.system()
    platform = 'Linux'

    def __init__(self, settings: Settings):
        super().__init__()
        self.chain_elements = []
        self._settings = settings

    @classmethod
    def get_platform_specific_chain(cls):
        """
        Returns the chain for the current platform.
        :rtype: ProcessingChain
        """
        # TODO: Recursive search (multi inheritance)
        # TODO: Respect settingstree (user could use another chain for his system)
        for subclass in cls.__subclasses__():
            if subclass.platform == platform.system():
                return subclass

    def register(self, chain_element):
        """
        This method adds the given chain_element to the internal list with chain_elements.
        :param chain_element:
        :return:
        """
        if not isinstance(chain_element, ChainElement):
            raise TypeError('chain_element needs to be an instance of chain.ChainElement!')

        self.chain_elements.append(chain_element)

        # Collect element specific settings from chain_element.
        chain_element_settings_subtree = chain_element.collect_settings()
        if chain_element_settings_subtree.has_children():
            self._settings.root.add_child(chain_element_settings_subtree)

    def run(self):
        """
        This method iterates through all registered chain_elements. It calls the process method and passes the output
        to the next chain element.
        """
        mid_result = ()

        for element in self.chain_elements:
            mid_result = element.process(*mid_result)
