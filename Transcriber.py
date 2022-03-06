from PIL import Image
from os import path, listdir
from StegImage import StegImage
import random


class Transcriber:

    def __init__(self, mode, image_folder_path, destination_folder_path):
        if not path.exists(image_folder_path):
            raise Exception("Image path is incorrect or does not exist!")
        self.mode = mode
        self.source_image_folder_path = image_folder_path
        self.destination_folder_path = destination_folder_path
        self.leftover = 0

    def init_images(self):
        # self.images = [StegImage(path.join(self.source_image_folder_path, image), path.join(self.destination_folder_path, image), self.mode) for image in listdir(self.source_image_folder_path)]
        self.images = [StegImage(path.join(self.source_image_folder_path, image), path.join(self.destination_folder_path, image), self.mode) for image in ["my-hero.jpeg", "demon-slayer.jpeg"]]
        # random.shuffle(self.images)
        # self.images = [StegImage(path.join(self.source_image_folder_path, image), path.join(self.destination_folder_path, image), self.mode) for image in listdir(self.source_image_folder_path)]
        random.shuffle(self.images)
        self.current_image_index = 0
        self.current_image = self.images[self.current_image_index]
        self.current_image.init_encoding(min(self.current_image.bits_that_can_store(0), self.total_bit_length), self.current_image_index)

    def can_fit_bytes(self, bytes_to_save):
        self.total_bit_length = bytes_to_save * 8
        self.init_images()

        can_fit = sum([image.bits_that_can_store(0) for image in self.images])
        return bytes_to_save * 8 <= can_fit
    

    def set_encoding(self, data_to_encode):
        bits_to_store = len(data_to_encode) * 8
        byte_index = 0
        print("Encoding: ", bits_to_store)
        
        while bits_to_store > 0:
            image_can_store = self.current_image.bits_that_can_store(self.leftover)
            if bits_to_store > image_can_store:
                print("storing full", self.current_image, image_can_store)
                self.leftover = self.current_image.encode_data(data_to_encode, byte_index, self.leftover)
                self.current_image.finish_encoding()

                # udpate lengths
                bits_to_store -= image_can_store
                self.total_bit_length -= image_can_store
                byte_index += image_can_store // 8

                # iterate current image
                self.current_image_index += 1
                self.current_image = self.images[self.current_image_index]
                self.current_image.init_encoding(min(image_can_store, self.total_bit_length), self.current_image_index)
            else:
                print("storing partial", self.current_image, bits_to_store)
                self.leftover = self.current_image.encode_data(data_to_encode, byte_index, self.leftover)
                self.total_bit_length -= bits_to_store
                bits_to_store = 0
        print("")

    def finish_encoding(self):
        self.current_image.finish_encoding()

