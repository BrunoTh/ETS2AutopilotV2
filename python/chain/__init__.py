import platform
from abc import ABC, abstractmethod
from settingstree import Settings, SettingsNode
from settingstree.widgets.nodewidgets import NodeSubtree
from chain import capturing, processing, controller
from chain.builtin import ChainElement, ProcessingResult
import logging

log = logging.getLogger(__name__)


class WebFunctionDoesNotExistException(Exception):
    pass


class ProcessingChain(ABC):
    # Use this chain if platform string matches platform.system()
    platform = 'Linux'

    def __init__(self, settings: Settings):
        super().__init__()
        self.chain_elements = []
        self._settings = settings
        self._web_functions = {}

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
        # But only add this collected subtree if it has children on it. This prevents useless empty nodes.
        if chain_element_settings_subtree.has_children():
            self._settings.root.add_child(chain_element_settings_subtree)

        # Register web functions
        # TODO: namespaces for web functions
        self._web_functions.update(chain_element.collect_web_functions())
        log.debug(f'Registed web functions: {[key for key in chain_element.collect_web_functions().keys()]}')

    async def call_web_function(self, name, kwargs):
        """
        Tries to find web functions with given `name` and executes it.
        :raises WebFunctionDoesNotExistException
        :param name: Name of web function.
        :param kwargs: Arguments for web function call.
        :return: Result of web function.
        """
        if name not in self._web_functions:
            raise WebFunctionDoesNotExistException

        return await self._web_functions[name](kwargs)

    def run(self) -> list:
        """
        This method iterates through all registered chain_elements. It calls the process method and passes the output
        to the next chain element.
        :return: list with data from chain members.
        """
        mid_result = ProcessingResult([], {})
        end_result = []

        for element in self.chain_elements:
            try:
                mid_result = element.process(*mid_result.args, **mid_result.kwargs)
                if mid_result.data_to_send:
                    end_result.append(mid_result.data_to_send)
            except TypeError as e:
                log.exception(f'Error in while processing ChainElement {element}.')

        return end_result

        # TODO: add field content_for_websocket to ProcessingResult. This than gets returned to the api which sends it
        #  to the browser via websocket.
        # TODO: find a way to send data via websocket from inside a chain_element.


class CVChainWindows(ProcessingChain):
    platform = 'Windows'

    def __init__(self, settings):
        super().__init__(settings)

        self.register(capturing.ImageGrabDevice())
        self.register(processing.ColorConversionPreProcessingUnit())
        self.register(processing.ROIPreProcessingUnit())
        self.register(processing.GrayscaleConversionPreProcessingUnit())
        # self.register(processing.CVLaneDetectionProcessingUnit())
        self.register(controller.VjoyController())


class CVChainLinux(ProcessingChain):
    platform = 'Linux'

    def __init__(self, settings):
        super().__init__(settings)

        self.register(capturing.PyscreenshotDevice())
        self.register(processing.ColorConversionPreProcessingUnit())
        self.register(processing.ROIPreProcessingUnit())
        self.register(processing.GrayscaleConversionPreProcessingUnit())
        self.register(processing.CVLaneDetectionProcessingUnit())
        # self.register()
