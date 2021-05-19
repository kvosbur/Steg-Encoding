from PIL import Image
import queue
from os import path


def overwrite_pixel_value(prev_value, value_to_hide):
    return (prev_value & 252) | value_to_hide


class Extractor:

    def __init__(self, image_path):
        if not path.exists(image_path):
            raise Exception("Image path is incorrect or does not exist!")
        self.image_path = image_path
        self._image = Image.open(image_path)
        self._pixels = self._image.load()
        self._decoding_queue = queue.Queue()
        self._internal_bytes = bytearray()
        self._x = 0
        self._y = 0

    def get_total_pixels(self):
        x, y = self._image.size
        # assuming that I am only changing rgb and not rgba
        return x * y * 3

    def _get_next_pixel(self):
        r, g, b = self._pixels[self._x, self._y]
        self._decoding_queue.put(r & 3)
        self._decoding_queue.put(g & 3)
        self._decoding_queue.put(b & 3)

    def decode_image(self, bytes_to_decode):
        while len(self._internal_bytes) < bytes_to_decode and not (self._x == self._image.size[0] and self._y == 0):
            self._get_next_pixel()
            self._y += 1
            if self._y == self._image.size[1]:
                self._x += 1
                self._y = 0
            self.get_encoding()
        return self._internal_bytes

    def get_encoding(self):
        while self._decoding_queue.qsize() > 4:
            val = 0
            val += self._decoding_queue.get() << 6
            val += self._decoding_queue.get() << 4
            val += self._decoding_queue.get() << 2
            val += self._decoding_queue.get()
            self._internal_bytes.append(val)
