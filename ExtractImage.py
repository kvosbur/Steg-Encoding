from email.mime import image
from PIL import Image
from os import path
import queue
from StegImage import StegImage

class ExtractImage:

    def __init__(self, image_path):
        if not path.exists(image_path):
            raise Exception("Image path is incorrect or does not exist!")
        self.image_path = image_path
        self._internal_bytes = bytearray()
        self._decoding_queue = queue.Queue()
        self.bits_read = 0
        self._x = 0
        self._y = 0

    def get_header(self):
        self._image = Image.open(self.image_path)
        self._pixels = self._image.load()
        header_data = self.decode_image(StegImage.header_size())
        mode = int.from_bytes(bytes(header_data[0]), 'big')
        self.image_number = int.from_bytes(bytes(header_data[1:3]), 'big')
        self.num_bits = int.from_bytes(bytes(header_data[3:9]), 'big')
        print(self._decoding_queue.qsize())
        self.bits_read -= StegImage.header_size() * 8
        self._internal_bytes = bytearray()

    def _get_next_pixel(self):
        r, g, b = self._pixels[self._x, self._y]
        self._decoding_queue.put(r & 3)
        self._decoding_queue.put(g & 3)
        self._decoding_queue.put(b & 3)
        self.bits_read += 6
        self._y += 1
        if self._y == self._image.size[1]:
            self._x += 1
            self._y = 0

    def get_encoding(self):
        while self._decoding_queue.qsize() >= 4:
            val = 0
            val += self._decoding_queue.get() << 6
            val += self._decoding_queue.get() << 4
            val += self._decoding_queue.get() << 2
            val += self._decoding_queue.get()
            self._internal_bytes.append(val)

    def decode_image(self, bytes_to_decode):
        while len(self._internal_bytes) < bytes_to_decode and not (self._x == self._image.size[0] and self._y == 0):
            self._get_next_pixel()
            
            self.get_encoding()
        
        return self._internal_bytes

    def decode_rest_of_image(self):
        print('\n\n', self.image_path)
        try:
            while self.bits_read != self.num_bits:
                self._get_next_pixel()
                self.get_encoding()
        except:
            print('caught exception')
        print("bits read", self.bits_read)
        print("bits expect", self.num_bits)
        print("queue size", self._decoding_queue.qsize())
        print("size", self._image.size, "x", self._x, "y", self._y)
        if self._decoding_queue.qsize() != 0:
            print("THIS IS NOT GOING TO WORK")
            exit()
        return self._internal_bytes

    def __repr__(self) -> str:
        return f"{self.image_path} {self.image_number}"
