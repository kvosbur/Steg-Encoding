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
        self.bits_read = 0
        self._x = 0
        self._y = 0
        self.val = 0
        self.offset = 0
        self.num_bits = 0

    def init_image(self):
        self._image = Image.open(self.image_path)
        self.size_x, self.size_y = self._image.size
        self._pixels = self._image.load()
    
    def close_image(self):
        self._image.close()
        self._image = None


    def get_header(self):
        header_data = self.decode_image(decode_header=True)
        mode = int.from_bytes(bytes(header_data[:1]), 'big')
        self.image_number = int.from_bytes(bytes(header_data[1:3]), 'big')
        self.num_bits = int.from_bytes(bytes(header_data[3:9]), 'big')
        self.bits_read -= StegImage.header_size() * 8
        self.header = header_data
        self._internal_bytes = bytearray()
        # print(self.image_path, self.size_x, self.size_y, self._image.size, self.num_bits)

    def get_final_offset(self, given_offset):
        self.init_image()
        offset = ((self.num_bits + (given_offset * 2)) % 8) // 2
        val = 0
        r, g, b = self._pixels[self.size_x - 1, self.size_y - 1]
        if offset == 1:
            val += ((b & 3) << 6)
        elif offset == 2:
            val += ((g & 3) << 6)
            val += ((b & 3) << 4)
        elif offset == 3:
            val += ((r & 3) << 6) 
            val += ((g & 3) << 4) 
            val += ((b & 3) << 2) 
        self.close_image()
        return offset, val

    def decode_image(self, decode_header = False):
        self.init_image()
        offset = self.offset
        val = self.val
        while not (self._x == self.size_x and self._y == 0):
            r, g, b = self._pixels[self._x, self._y]
            if offset == 0:
                val += ((r & 3) << 6) 
                val += ((g & 3) << 4) 
                val += ((b & 3) << 2) 
                offset = 3
            elif offset == 1:
                val += ((r & 3) << 4) 
                val += ((g & 3) << 2)
                val += (b) & 3
                self._internal_bytes.append(val)
                val = 0
                offset = 0
            elif offset == 2:
                val += ((r & 3) << 2)
                val += (g) & 3
                self._internal_bytes.append(val)
                val = 0
                val += ((b & 3) << 6)
                offset = 1
            elif offset == 3:
                val += (r) & 3
                self._internal_bytes.append(val)
                val = 0
                val += ((g & 3) << 6)
                val += ((b & 3) << 4)
                offset = 2
            
            self.offset = offset
            self.val = val

            self.bits_read += 6
            self._y += 1
            if self._y == self.size_y:
                self._x += 1
                self._y = 0

            if decode_header and len(self._internal_bytes) == StegImage.header_size():
                self.close_image()
                return self._internal_bytes
            elif not decode_header and self.bits_read >= self.num_bits:
                self.close_image()
                return self._internal_bytes

        print("bits read", self.bits_read, "out of:", self.num_bits)
        if offset != 0:
            print("NEED TO WORRY ABOUT OVERLAP")
            exit()

    def __repr__(self) -> str:
        return f"{self.image_path} {self.image_number}"
