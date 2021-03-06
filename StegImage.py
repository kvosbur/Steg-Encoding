from email import header
from PIL import Image
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

    def __repr__(self) -> str:
        return f"StegImage {self.source_image_path}"
        
    @staticmethod
    def header_size():
        return 9

    def total_bits_that_can_store(self) -> int:
        image = Image.open(self.source_image_path)
        x, y = image.size
        image.close()
        # assuming that I am only changing rgb and not rgba
        return (x * y * 3 * 2) - (StegImage.header_size() * 8)

    def bits_that_can_store(self) -> int:
        return self.total_bits_that_can_store() - self.bits_stored

    def get_header_info(self, image_number):
        first_image_bit_mask = 128 if image_number == 0 else 0
        version_number = (self.mode | first_image_bit_mask).to_bytes(1, 'big')
        image_number_bytes = image_number.to_bytes(2, 'big')
        length_bytes = self.bit_length_to_store.to_bytes(6, 'big')
        return version_number + image_number_bytes + length_bytes

    def init_encoding(self, bit_length_to_store, image_number):
        self._image = Image.open(self.source_image_path)
        self.size_x, self.size_y = self._image.size
        self._pixels = self._image.load()
        self.bit_length_to_store = bit_length_to_store

        # store header info
        self.image_number = image_number
        data = self.get_header_info(image_number)
        self.encode_data(data, 0, 0, header_offset=0)
        self.bits_stored = 0

    def close_image(self):
        self._image.close()

    def increment(self, x, y):
        y += 1
        if y == self.size_y:
            x += 1
            y = 0
            if x == self.size_x:
                return None, None
        return x,y

    def encode_data_with_finish(self, data, byte_index, byte_offset, header_offset = 72):
        self.encode_data(data, byte_index, byte_offset, header_offset)
        self.finish_encoding()

    def initial_offset(self, data, byte_index, offset, header_offset = 72):
        if offset == 0:
            return byte_index
        pixel_start = ((self.bits_stored + header_offset) // 6)
        pixel_x = pixel_start // self.size_y
        pixel_y = pixel_start % self.size_y
        if (self.bits_stored % 6) // 2 != 0:
            print("ASSUMPTION BROKEN")
            print(self.bits_stored)
            print((self.bits_stored % 6) // 2)
            print(offset)
            exit()
        byte = data[byte_index]
        second = byte >> 4 & 3
        third = byte >> 2 & 3
        fourth = byte & 3
        prev_r, prev_g, prev_b = self._pixels[pixel_x, pixel_y]
        if offset == 2:
            next_value = (overwrite_pixel_value(prev_r, fourth),
                          prev_g,
                          prev_b)
            self._pixels[pixel_x, pixel_y] = next_value
            self.bits_stored += 2
            return byte_index + 1
        elif offset == 4:
            next_value = (overwrite_pixel_value(prev_r, third),
                          overwrite_pixel_value(prev_g, fourth),
                          prev_b)
            self._pixels[pixel_x, pixel_y] = next_value
            self.bits_stored += 4
            return byte_index + 1
        elif offset == 6:
            next_value = (overwrite_pixel_value(prev_r, second),
                          overwrite_pixel_value(prev_g, third),
                          overwrite_pixel_value(prev_b, fourth))
            self._pixels[pixel_x, pixel_y] = next_value
            self.bits_stored += 6
            return byte_index + 1
        return byte_index

    def encode_data(self, data, byte_index, byte_offset, header_offset = 72):
        new_byte_index = self.initial_offset(data, byte_index, byte_offset)
        pixel_start = ((self.bits_stored + header_offset) // 6)
        pixel_x = pixel_start // self.size_y
        pixel_y = pixel_start % self.size_y
        pixel_offset = (self.bits_stored % 6) // 2
        for byte in data[new_byte_index:]:
            first = byte >> 6
            second = byte >> 4 & 3
            third = byte >> 2 & 3
            fourth = byte & 3
            prev_r, prev_g, prev_b = self._pixels[pixel_x, pixel_y]
            if pixel_offset == 0:
                next_value = ((prev_r & 252) | first,
                          (prev_g & 252) | second,
                          (prev_b & 252) | third)
                self._pixels[pixel_x, pixel_y] = next_value
                # pixel_x, pixel_y = self.increment(pixel_x, pixel_y)  # (inlining)
                pixel_y += 1
                if pixel_y == self.size_y:
                    pixel_x += 1
                    pixel_y = 0
                    if pixel_x == self.size_x:
                        self.bits_stored += 6
                        return 2
                # if pixel_x is None:
                #     self.bits_stored += 6
                #     return 2

                prev_r, prev_g, prev_b = self._pixels[pixel_x, pixel_y]
                next_value = ((prev_r & 252) | fourth,
                          prev_g,
                          prev_b)
                self._pixels[pixel_x, pixel_y] = next_value
                pixel_offset = 1

            elif pixel_offset == 1:
                next_value = (prev_r,
                          (prev_g & 252) | first,
                          (prev_b & 252) | second)
                self._pixels[pixel_x, pixel_y] = next_value
                # pixel_x, pixel_y = self.increment(pixel_x, pixel_y)  # (inlining)
                pixel_y += 1
                if pixel_y == self.size_y:
                    pixel_x += 1
                    pixel_y = 0
                    if pixel_x == self.size_x:
                        self.bits_stored += 4
                        return 4
                # if pixel_x is None:
                #     self.bits_stored += 4
                #     return 4

                prev_r, prev_g, prev_b = self._pixels[pixel_x, pixel_y]
                next_value = ((prev_r & 252) | third,
                          (prev_g & 252) | fourth,
                          prev_b)
                self._pixels[pixel_x, pixel_y] = next_value
                pixel_offset = 2

            elif pixel_offset == 2:
                next_value = (prev_r,
                          prev_g,
                          (prev_b & 252) | first)
                self._pixels[pixel_x, pixel_y] = next_value
                # pixel_x, pixel_y = self.increment(pixel_x, pixel_y)  # (inlining)
                pixel_y += 1
                if pixel_y == self.size_y:
                    pixel_x += 1
                    pixel_y = 0
                    if pixel_x == self.size_x:
                        self.bits_stored += 2
                        return 6
                # if pixel_x is None:
                #     self.bits_stored += 2
                #     return 6

                prev_r, prev_g, prev_b = self._pixels[pixel_x, pixel_y]
                next_value = ((prev_r & 252) | second,
                          (prev_g & 252) | third,
                          (prev_b & 252) | fourth)
                self._pixels[pixel_x, pixel_y] = next_value
                pixel_offset = 0
                # pixel_x, pixel_y = self.increment(pixel_x, pixel_y)  # (inlining)
                pixel_y += 1
                if pixel_y == self.size_y:
                    pixel_x += 1
                    pixel_y = 0
                    if pixel_x == self.size_x:
                        return 0

            self.bits_stored += 8
            if pixel_x is None:
                return 0
        return 0

    def finish_encoding(self):
        print("saving image", self.destination_image_path)
        self._image.save(self.destination_image_path, format="PNG")
        self._image.close()

