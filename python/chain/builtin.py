from . import ProcessingChain
from . import capturing, processing, controller


class CVChainWindows(ProcessingChain):
    platform = 'Windows'

    def __init__(self, settings):
        super().__init__(settings)

        self.register(capturing.ImageGrabDevice())
        self.register(processing.ColorConversionPreProcessingUnit())
        self.register(processing.ROIPreProcessingUnit())
        self.register(processing.CVLaneDetectionProcessingUnit())
        self.register(controller.VjoyController())
