from PIL import Image
import queue
from os.path import splitext


def overwrite_pixel_value(prev_value, value_to_hide):
    return (prev_value & 252) | value_to_hide

class StegImage:
    def __init__(self, source_image_path, destination_image_path, mode) -> None:
        self.source_image_path = source_image_path
        base, _ = splitext(destination_image_path)
        self.destination_image_path = base + ".png"
        self.mode = mode
        self.bits_stored = 0
        self._x = 0
        self._y = 0

    def __repr__(self) -> str:
        return f"{self.source_image_path}"
        
    @staticmethod
    def header_size():
        return 9

    def total_bits_that_can_store(self) -> int:
        image = Image.open(self.source_image_path)
        x, y = image.size
        image.close()
        # assuming that I am only changing rgb and not rgba
        return (x * y * 3 * 2) - (StegImage.header_size() * 8)

    def bits_that_can_store(self, queue_size) -> int:
        return self.total_bits_that_can_store() - self.bits_stored - (queue_size * 2)

    def get_header_info(self, image_number):
        
        first_image_bit_mask = 128 if image_number == 0 else 0
        version_number = (self.mode | first_image_bit_mask).to_bytes(1, 'big')
        image_number_bytes = image_number.to_bytes(2, 'big')
        length_bytes = self.bit_length_to_store.to_bytes(6, 'big')
        print(version_number + image_number_bytes + length_bytes)
        return version_number + image_number_bytes + length_bytes

    def init_encoding(self, bit_length_to_store, image_number):
        print(self.source_image_path, image_number)
        self._image = Image.open(self.source_image_path)
        self._pixels = self._image.load()
        self.bit_length_to_store = bit_length_to_store
        print("amount to store", bit_length_to_store)

        # store header info
        data = self.get_header_info(image_number)
        encoding_queue = queue.Queue()
        for byte in data:
            encoding_queue.put(byte >> 6)
            encoding_queue.put(byte >> 4 & 3)
            encoding_queue.put(byte >> 2 & 3)
            encoding_queue.put(byte & 3)
        self.set_next_pixels(encoding_queue)
        self.bits_stored = 0

    def set_next_pixels(self, encoding_queue):
        while encoding_queue.qsize() >= 3:
            prev_r, prev_g, prev_b = self._pixels[self._x, self._y]

            next_value = (overwrite_pixel_value(prev_r, encoding_queue.get()),
                          overwrite_pixel_value(prev_g, encoding_queue.get()),
                          overwrite_pixel_value(prev_b, encoding_queue.get()))
            self._pixels[self._x, self._y] = next_value
            self.bits_stored += 6
            self._y += 1
            if self._y == self._image.size[1]:
                self._x += 1
                self._y = 0
                if self._x == self._image.size[0]:
                    break

    def finish_encoding(self, encoding_queue):
        print("bits stored before", self.bits_stored)
        if self.bits_that_can_store(0) != 0:
            while encoding_queue.qsize() % 3 != 0:
                encoding_queue.put(0)
            print("ADDING ", encoding_queue.qsize())
            self.set_next_pixels(encoding_queue)
        print("bits stored", self.bits_stored)
        print('\n')
        self._image.save(self.destination_image_path, format="PNG")

