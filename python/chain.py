from logging import Logger
from abc import ABC, abstractmethod
import platform
from . import capturing
from . import processing
from . import controller
from .settingstree import Settings, SettingsNode

log = Logger(__name__)


class ChainElement(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._settings_node = SettingsNode(key=self.__class__.__name__)

    def collect_settings(self) -> SettingsNode:
        """
        This methods searches for instances of SettingsNodes and adds them to self._settings_node.
        :return: self._settings_node
        """
        for attribute in dir(self):
            if isinstance(getattr(self, attribute), SettingsNode):
                self._settings_node.add_child(getattr(self, attribute))

        return self._settings_node

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
        if chain_element.collect_settings():
            self._settings.root.add_child(chain_element.collect_settings())

    def run(self):
        """
        This method iterates through all registered chain_elements. It calls the process method and passes the output
        to the next chain element.
        """
        mid_result = ()

        for element in self.chain_elements:
            mid_result = element.process(*mid_result)


class CVChainWindows(ProcessingChain):
    platform = 'Windows'

    def __init__(self, settings):
        super().__init__(settings)

        self.register(capturing.ImageGrabDevice())
        self.register(processing.ColorConversionPreProcessingUnit())
        self.register(processing.ROIPreProcessingUnit())
        self.register(processing.CVLaneDetectionProcessingUnit())
        self.register(controller.VjoyController())
