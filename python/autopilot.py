import platform
from chain.builtin import ProcessingChain
from settingstree import Settings
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    log.debug(f'Running on {platform.system()}')
    try:
        settings = Settings()
        platform_specific_chain = ProcessingChain.get_platform_specific_chain()
        platform_specific_chain(settings).run()
    except (AttributeError, TypeError):
        log.exception('Sorry! Your platform is not supported.')
