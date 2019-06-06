from logging import Logger
from settingstree import Settings
import responder
from chain import ProcessingChain

log = Logger(__name__)
settings = Settings()
responder_api = responder.API()
processing_chain = None

# APP STATES
ap_active = False


class WebSocketMixin:
    ws = None

    def send_via_websocket(self, msg):
        pass


@responder_api.on_event('startup')
async def initialize_chain():
    global processing_chain
    processing_chain = ProcessingChain.get_platform_specific_chain()

    if not processing_chain:
        log.error('Your platform is currently not supported.')


@responder_api.route('/')
async def page_index(request, response):
    return responder_api.template('index.html')


@responder_api.route('/settings')
async def page_settings(request, response):
    sub_tree = settings.root.get_sub_tree()
    # TODO: What's a good way to render the form structure?
    return responder_api.template('settings.html', form_html=sub_tree)


@responder_api.route('/ws/index', websocket=True)
async def index_route(ws):
    """
    Controls the autopilot. Possible commands are: activate, deactivate
    :param ws:
    :return:
    """

    @responder_api.background.task
    async def run_autopilot_loop():
        while ap_active:
            processing_chain.run()

    await ws.accept()

    while True:
        received_json = await ws.receive_json()
        cmd = received_json['cmd']

        # TODO: figure out better way. Maybe use an interface where you can register the commands.
        if cmd == 'activate':
            ap_active = True
            # TODO: Does this actually work?
            await run_autopilot_loop()
        elif cmd == 'deactivate':
            ap_active = False


@responder_api.route('/ws/ap_image', websocket=True)
async def apimage_route(ws):
    pass


@responder_api.route('/ws/settings', websocket=True)
async def settings_route(ws):
    """
    Websocket for settings. Takes json with elements: cmd, fqid, value
    :param ws: websocket
    """

    # WARNING!
    # I'm just goofing around. I'm not sure if this is a good way. If a way at all.
    # Another idea is to use an adapter class that executes a method which is registered to a command.
    # TODO: Needs some more brainstorming. Maybe a brain-tornado.

    await ws.accept()

    while True:
        received_json = await ws.receive_json()
        cmd = received_json['cmd']
        fqid = received_json['fqid']
        value = received_json.get('value')

        response = {'status': 500, 'response': ''}

        try:
            if cmd == 'get':
                response['status'] = 200
                response['response'] = settings.root.get_value_of_child(fqid)
            elif cmd == 'set':
                if not value:
                    raise AttributeError('Value is not set.')

                settings.root.set_value_of_child(fqid, value)
                response['status'] = 200
                response['response'] = settings.root.get_value_of_child(fqid)
        except Exception as e:
            log.exception('Error in settings websocket.')
            response['status'] = 500
            response['response'] = str(e)

        await ws.send_json(response)
