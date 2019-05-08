from logging import Logger
import json
import pathlib

log = Logger(__name__)
# Path object of python/ directory.
BASE_PATH = pathlib.Path(__file__).parent
DEFAULT_NAME = 'settings.json'


# TODO: singleton?
class Settings:
    INPUT_DEVICE_TYPE = 'controller_type'
    INPUT_DEVICE_TYPE_KEYBOARD = 0
    INPUT_DEVICE_TYPE_GAMEPAD = 1
    INPUT_DEVICE_TYPE_WHEEL = 2

    INPUT_DEVICE_AXIS_STEERING = ''
    VIRTUAL_CONTROLLER_ID = 'controller_id'  # id of the controller (e.g. vjoy device id)
    VIEWPORT_ROI_X1 = 'viewport_roi_x1'
    VIEWPORT_ROI_X2 = 'viewport_roi_x2'
    VIEWPORT_ROI_Y1 = 'viewport_roi_y1'
    VIEWPORT_ROI_Y2 = 'viewport_roi_y2'

    def __init__(self, filename=DEFAULT_NAME):
        self.filename = filename
        self._file_object = None
        self._parsed_json = dict()

        try:
            with open(self.filename) as f:
                self._parsed_json = json.load(self._file_object)
        except Exception:
            log.exception(f'Error while opening {self.filename}.')

    def get_file_object(self):
        if not self._file_object:
            self._file_object = open(self.filename, 'r')

        return self._file_object

    def close_file_object(self):
        if self._file_object:
            try:
                self._file_object.close()
                self._file_object = None
            except Exception:
                log.exception('Error while closing Settings.file_object.')

    def parse_json(self):
        self._parsed_json = json.load(self.get_file_object())
        self.close_file_object()

    def dump_json(self):
        json.dump(self._parsed_json, self.get_file_object())
        self.close_file_object()

    def get_value(self, key):
        self.parse_json()
        # TODO: Pass KeyError or wrap error with own SettingsKeyError Exception?
        return self._parsed_json[key]

    def write_value(self, key, value):
        self.parse_json()
        self._parsed_json[key] = value
        self.dump_json()

    def delete_key(self, key):
        self.parse_json()
        # TODO: Pass KeyError or wrap error with own SettingsKeyError Exception?
        self._parsed_json.pop(key)
        self.dump_json()
