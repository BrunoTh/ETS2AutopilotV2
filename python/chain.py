from logging import Logger
from abc import ABC, abstractmethod
from . import capturing
from . import processing
from . import controller

log = Logger(__name__)


class ChainElement(ABC):
    @abstractmethod
    def process(self, *args):
        """

        :param args:
        :return:
        """


class ProcessingChain(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chain_elements = []

    def register(self, chain_element):
        """
        This method adds the given chain_element to the internal list with chain_elements.
        :param chain_element:
        :return:
        """
        if not isinstance(chain_element, ChainElement):
            raise TypeError('chain_element needs to be an instance of chain.ChainElement!')

        self.chain_elements.append(chain_element)

    def run(self):
        """
        This method iterates through all registered chain_elements. It calls the process method and passes the output
        to the next chain element.
        """
        mid_result = ()

        for element in self.chain_elements:
            mid_result = element.process(*mid_result)


class CVChainWindows(ProcessingChain):
    def __init__(self):
        super().__init__()

        self.register(capturing.ImageGrabDevice())
        self.register(processing.ColorConversionPreProcessingUnit())
        self.register(processing.ROIPreProcessingUnit())
        self.register(processing.CVLaneDetectionProcessingUnit())
        self.register(controller.VjoyController(0))  # TODO: get vjoy controller from settings
