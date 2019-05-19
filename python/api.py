from logging import Logger
from .settingstree import Settings
import responder
import json

log = Logger(__name__)
responder_api = responder.API()


class WebSocketMixin:
    ws = None

    def send_via_websocket(self, msg):
        pass


@responder_api.route('/settings', websocket=True)
async def modify_settings(ws):
    """
    Websocket for settings. Takes json with elements:
    cmd: string, parameters: list
    :param ws:
    :return:
    """

    # WARNING!
    # I'm just goofing around. I'm not sure if this is a good way. If a way at all.
    # Another idea is to use an adapter class that executes a method which is registered to a command.
    # TODO: Needs some more brainstorming. Maybe a brain-tornado.

    await ws.accept()
    while True:
        received_json = await ws.receive_json()
        cmd = received_json['cmd']
        params = received_json['paramters']
        response = {'status': 500, 'response': ''}

        try:
            if cmd == 'get':
                response['status'] = 200
                response['response'] = Settings().get_value(*params)
            elif cmd == 'set':
                Settings().write_value(*params)
                response['status'] = 200
                response['response'] = ''
        except Exception as e:
            log.exception('Error in settings websocket.')
            response['status'] = 500
            response['response'] = str(e)

        await ws.send_json(response)
