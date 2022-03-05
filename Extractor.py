from PIL import Image
import queue
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
        for image in sorted_images:
            data += image.decode_rest_of_image()
            print(len(data) * 8)

        return data
