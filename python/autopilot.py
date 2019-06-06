import platform
import logging
import api

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    log.debug(f'Running on {platform.system()}')

    # Start the API
    api.responder_api.run()
