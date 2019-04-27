from logging import Logger

log = Logger(__name__)


class WebSocketMixin:
    ws = None

    def send_via_websocket(self, msg):
        pass
