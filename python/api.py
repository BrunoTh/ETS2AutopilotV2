from logging import Logger
from settingstree import Settings
import responder
import json

log = Logger(__name__)
settings = Settings()
responder_api = responder.API()


class WebSocketMixin:
    ws = None

    def send_via_websocket(self, msg):
        pass


"""
settings_route:
    get: return all available SettingsNodes

settings_route_ws:
    cmd: get/put
    key: SettingsNode.fqid
    value: SettingsNode.value
"""


@responder_api.route('/')
async def page_index(request, response):
    return responder_api.template('index.html')


@responder_api.route('/settings')
async def page_settings(request, response):
    sub_tree = settings.root.get_sub_tree()
    # TODO: What's a good way to render the form structure?
    return responder_api.template('settings.html', form_fields=sub_tree)


@responder_api.route('/ws/index', websocket=True)
async def index_route(ws):
    pass


@responder_api.route('/ws/ap_image', websocket=True)
async def apimage_route(ws):
    pass


@responder_api.route('/ws/settings', websocket=True)
async def settings_route(ws):
    """
    Websocket for settings. Takes json with elements: cmd, key, value
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
