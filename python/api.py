from logging import Logger
from settingstree import Settings
import responder
from chain import ProcessingChain
from json.decoder import JSONDecodeError
from threading import Thread, Lock
import sys

log = Logger(__name__)
settings = Settings()
responder_api = responder.API()
processing_thread = None


# TODO: move this somewhere else
class ProcessingThread(Thread):
    # TODO: move these to instance namespace?
    lock = Lock()
    ap_active = False

    def __init__(self, processing_chain: ProcessingChain):
        super().__init__(daemon=True)

        self.processing_chain = processing_chain

    def start(self) -> None:
        with ProcessingThread.lock:
            ProcessingThread.ap_active = True

        super().start()

    def stop(self):
        with ProcessingThread.lock:
            ProcessingThread.ap_active = False

    def run(self) -> None:
        while ProcessingThread.ap_active:
            self.processing_chain.run()
            # TODO: collect results of chain elements and send them (as one json) via websocket


@responder_api.route(before_request=True, websocket=True)
async def prepare_response(ws):
    await ws.accept()


@responder_api.on_event('startup')
async def initialize_chain():
    PlatformProcessingChain = ProcessingChain.get_platform_specific_chain()
    processing_chain = PlatformProcessingChain(settings)

    if not processing_chain:
        log.error('Your platform is currently not supported.')
        sys.exit(1)

    # Load settings after chain initialized tree.
    settings.load()

    global processing_thread
    processing_thread = ProcessingThread(processing_chain)


@responder_api.route('/')
async def page_index(request, response):
    response.html = responder_api.template('index.html')


@responder_api.route('/settings')
async def page_settings(request, response):
    settings_form = settings.root.render_element()
    response.html = responder_api.template('settings.html', form_html=settings_form)


@responder_api.route('/ws/index', websocket=True)
async def index_route(ws):
    """
    Controls the autopilot. Possible commands are: activate, deactivate
    :param ws:
    :return:
    """

    while True:
        received_json = await ws.receive_json()
        cmd = received_json['cmd']

        # TODO: figure out better way. Maybe use an interface where you can register the commands.
        if cmd == 'activate':
            processing_thread.start()
        elif cmd == 'deactivate':
            processing_thread.stop()


@responder_api.route('/ws/ap_image', websocket=True)
async def apimage_route(ws):
    pass


@responder_api.route('/ws/settings', websocket=True)
async def settings_route(ws):
    """
    Websocket for settings. Takes json with elements: cmd, fqid, value.
    Sends json with status, fqid, value.
    :param ws: websocket
    """

    while True:
        # Try to receive json and catch exception if data is not valid json.
        try:
            received_json = await ws.receive_json()
        except JSONDecodeError:
            log.exception('Received message is not valid json!')
            continue

        cmd = received_json['cmd']
        fqid = received_json['fqid']
        value = received_json.get('value')

        response = {'status': 500, 'fqid': fqid, 'value': ''}

        try:
            # Send back the value of fqid.
            if cmd == 'get':
                response['status'] = 200
                response['value'] = settings.root.get_value_of_child(fqid)
            # Set value of fqid and send it back.
            elif cmd == 'set':
                if not value:
                    raise AttributeError('Value is not set.')

                settings.root.set_value_of_child(fqid, value)
                response['status'] = 200
                response['value'] = settings.root.get_value_of_child(fqid)

                settings.dump()
        except Exception as e:
            log.exception('Error in settings websocket.')
            response['status'] = 500
            response['value'] = str(e)

        await ws.send_json(response)
