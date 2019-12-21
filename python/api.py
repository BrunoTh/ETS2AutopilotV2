from logging import Logger
from settingstree import Settings
import responder
from starlette.websockets import WebSocketDisconnect, WebSocket, WebSocketState
from chain import ProcessingChain, WebFunctionDoesNotExistException
from json.decoder import JSONDecodeError
from threading import Thread, Lock
from collections import defaultdict
import sys
import asyncio

log = Logger(__name__)
settings = Settings()
responder_api = responder.API()

PlatformProcessingChain = ProcessingChain.get_platform_specific_chain()
processing_chain = PlatformProcessingChain(settings)

if not processing_chain:
    log.error('Your platform is currently not supported.')
    sys.exit(1)

# Load settings after chain initialized tree.
settings.load()


# TODO: move this somewhere else
class ProcessingThread(Thread):
    # TODO: move these to instance namespace?
    lock = Lock()
    ap_active = False
    instance = None

    def __init__(self, processing_chain: ProcessingChain):
        super().__init__(daemon=True)

        self.processing_chain = processing_chain
        self.stopped = False

    @classmethod
    def get_instance(cls, processing_chain: ProcessingChain):
        if not cls.instance or cls.instance.stopped:
            cls.instance = cls(processing_chain)

        return cls.instance

    def start(self) -> None:
        # Thread is already running.
        if self.is_alive():
            return

        with ProcessingThread.lock:
            ProcessingThread.ap_active = True

        super().start()

    def stop(self):
        with ProcessingThread.lock:
            ProcessingThread.ap_active = False

    def run(self) -> None:
        try:
            while ProcessingThread.ap_active:
                result = self.processing_chain.run()
                # Test: Send message to clients from inside the thread. (Is this even legal?)

                for element in result:
                    # TODO: find format for element
                    asyncio.run(ws_connection_pool.send_json('/ws/index', element))
        finally:
            self.stopped = True
            # TODO: set ap_active to False?


# TODO: move this somewhere else
class WSConnectionPool:
    def __init__(self):
        self._connection_pool = defaultdict(list)

    def _cleanup_closed_connections(self):
        for path in self._connection_pool:
            for ws_conn in self._connection_pool[path]:
                if ws_conn.client_state == WebSocketState.DISCONNECTED or \
                        ws_conn.application_state == WebSocketState.DISCONNECTED:
                    # TODO: maybe we need to close the connection to the client sometimes.
                    self.remove_connection(ws_conn)

    def add_connection(self, ws: WebSocket):
        if not isinstance(ws, WebSocket):
            raise TypeError('ws needs to be an instance of starlette.websockets.Websocket.')

        if ws not in self._connection_pool[ws.url.path]:
            self._connection_pool[ws.url.path].append(ws)

    def remove_connection(self, ws: WebSocket):
        self._connection_pool[ws.url.path].remove(ws)

    async def send_text(self, path_or_websocket, *args, **kwargs):
        if isinstance(path_or_websocket, WebSocket):
            path = path_or_websocket.url.path
        else:
            path = path_or_websocket

        self._cleanup_closed_connections()

        for ws_conn in self._connection_pool[path]:
            try:
                await ws_conn.send_text(*args, **kwargs)
            except RuntimeError:
                # Gets raised when trying to send to an already closed connection.
                log.exception('')

    async def send_bytes(self, path_or_websocket, *args, **kwargs):
        if isinstance(path_or_websocket, WebSocket):
            path = path_or_websocket.url.path
        else:
            path = path_or_websocket

        self._cleanup_closed_connections()

        for ws_conn in self._connection_pool[path]:
            try:
                await ws_conn.send_bytes(*args, **kwargs)
            except RuntimeError:
                # Gets raised when trying to send to an already closed connection.
                log.exception('')

    async def send_json(self, path_or_websocket, *args, **kwargs):
        if isinstance(path_or_websocket, WebSocket):
            path = path_or_websocket.url.path
        else:
            path = path_or_websocket

        self._cleanup_closed_connections()

        for ws_conn in self._connection_pool[path]:
            try:
                await ws_conn.send_json(*args, **kwargs)
            except RuntimeError:
                # Gets raised when trying to send to an already closed connection.
                log.exception('')


ws_connection_pool = WSConnectionPool()


@responder_api.route(before_request=True, websocket=True)
async def prepare_response(ws):
    await ws.accept()
    # Add connection to connection pool.
    ws_connection_pool.add_connection(ws)


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
            try:
                ProcessingThread.get_instance(processing_chain).start()
            except RuntimeError:
                log.exception('')
        elif cmd == 'deactivate':
            try:
                ProcessingThread.get_instance(processing_chain).stop()
            except RuntimeError:
                log.exception('')


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

        # Send changes to all websocket connections.
        await ws_connection_pool.send_json(ws, response)


@responder_api.route('/ws/web_functions', websocket=True)
async def web_functions_route(ws):
    """
    Websocket endpoint for web functions. Call functions in settings nodes by name. They may also return something.
    :param ws: websocket
    """
    while True:
        try:
            received_json = await ws.receive_json()
        except JSONDecodeError:
            log.exception('Received message is not valid json!')
            continue

        function_name = received_json['function_name']
        function_arguments = received_json.get('function_arguments', {})

        response = {'status': 500, 'function_name': function_name, 'function_arguments': function_arguments,
                    'result': None}

        try:
            function_result = await processing_chain.call_web_function(function_name, function_arguments)
            response['status'] = 200
            response['result'] = function_result
        except WebFunctionDoesNotExistException:
            response['status'] = 500
            response['result'] = 'The web function does not exist.'
        except Exception as e:
            log.exception('Error in settings websocket.')
            response['status'] = 500
            response['result'] = str(e)

        await ws_connection_pool.send_json(ws, response)
