from PIL import Image
import queue
from os import path


def overwrite_pixel_value(prev_value, value_to_hide):
    return (prev_value & 252) | value_to_hide


class Transcriber:

    def __init__(self, image_path):
        if not path.exists(image_path):
            raise Exception("Image path is incorrect or does not exist!")
        self.image_path = image_path
        self._image = Image.open(image_path)
        self._pixels = self._image.load()
        self._encoding_queue = queue.Queue()
        self._x = 0
        self._y = 0

    @staticmethod
    def bytes_for_size(amount):
        bits = bin(amount).replace('0b', '')
        return len(bits) // 8 + 1

    def get_total_pixels(self):
        x, y = self._image.size
        # assuming that I am only changing rgb and not rgba
        return x * y * 3

    def _set_next_pixels(self):
        while self._encoding_queue.qsize() >= 3:
            prev_r, prev_g, prev_b = self._pixels[self._x, self._y]
            # print(self._x)
            # print(self._y)
            # print(self._pixels[self._x, self._y])

            next_value = (overwrite_pixel_value(prev_r, self._encoding_queue.get()),
                          overwrite_pixel_value(prev_g, self._encoding_queue.get()),
                          overwrite_pixel_value(prev_b, self._encoding_queue.get()))
            self._pixels[self._x, self._y] = next_value
            # print(next_value)
            self._y += 1
            if self._y == self._image.size[1]:
                self._x += 1
                self._y = 0

    def set_encoding(self, data_to_encode):
        for byte in data_to_encode:
            self._encoding_queue.put(byte >> 6)
            self._encoding_queue.put(byte >> 4 & 3)
            self._encoding_queue.put(byte >> 2 & 3)
            self._encoding_queue.put(byte & 3)
            self._set_next_pixels()

    def finish_encoding(self, final_path):
        while self._encoding_queue.qsize() != 3:
            self._encoding_queue.put(0)
        self._set_next_pixels()
        self._image.save(final_path)
