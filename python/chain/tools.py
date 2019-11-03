from base64 import b64encode
import cv2


def encode_frame_to_base64(frame, format='.jpg'):
    return b64encode(cv2.imencode(format, frame)[1]).decode('utf-8')
