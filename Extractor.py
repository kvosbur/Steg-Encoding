from os import path, listdir
from ExtractImage import ExtractImage


def overwrite_pixel_value(prev_value, value_to_hide):
    return (prev_value & 252) | value_to_hide


class Extractor:

    def __init__(self, image_folder):
        if not path.exists(image_folder):
            raise Exception("Image path is incorrect or does not exist!")
        self.image_folder = image_folder

    def load_images(self):
        self.images = [ExtractImage(path.join(self.image_folder, image)) for image in listdir(self.image_folder)]
        [image.get_header() for image in self.images]
        sorted_images = sorted(self.images, key=lambda image: image.image_number)
        print(sorted_images)

        data = bytearray()
        prev_offset = 0
        prev_val = 0
        for index, image in enumerate(sorted_images):
            image.offset = prev_offset
            image.val = prev_val
            data += image.decode_image()
            prev_offset = image.offset
            prev_val = image.val
            print(image, image.bits_read, prev_val, prev_offset, index / len(sorted_images))

        return data
