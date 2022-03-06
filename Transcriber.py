from concurrent.futures import process
from PIL import Image
from os import path, listdir
from StegImage import StegImage
from multiprocessing import Process, Pool
import random


class Transcriber:

    POOL_SIZE = 6

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
        self.current_image.init_encoding(min(self.current_image.bits_that_can_store(), self.total_bit_length), self.current_image_index)

    def can_fit_bytes(self, bytes_to_save):
        self.total_bit_length = bytes_to_save * 8
        self.init_images()

        can_fit = sum([image.bits_that_can_store() for image in self.images])
        print("can fit:", can_fit)
        return bytes_to_save * 8 <= can_fit

    def choose_needed_images(self, required_bytes):
        choices = [image for image in listdir(self.source_image_folder_path)]
        self.total_bit_length = required_bytes * 8
        required_bits = self.total_bit_length
        self.images = []
        while required_bits > 0:
            next_image = random.choice(choices)
            self.images.append(StegImage(path.join(self.source_image_folder_path, next_image), path.join(self.destination_folder_path, str(len(self.images)) + next_image), self.mode))
            temp = sum([image.bits_that_can_store() for image in self.images])
            print("current total:", temp, temp / 8, len(self.images), next_image)
            required_bits -= self.images[-1].bits_that_can_store()
        
        print(len(self.images))
        self.current_image_index = 0
        self.current_image = self.images[self.current_image_index]
        self.current_image.init_encoding(min(self.current_image.bits_that_can_store(), self.total_bit_length), self.current_image_index)
    
    @staticmethod
    def do_parallel_images(*args):
        for (image_source_path, image_destination_path, mode, bit_length_to_store, image_number, max_images, data_to_encode, byte_index, byte_offset) in args:
            # print("Going through image", image_source_path, image_number)
            image = StegImage(image_source_path, image_destination_path, mode)
            image.init_encoding(bit_length_to_store, image_number)
            image.encode_data_with_finish(data_to_encode, byte_index, byte_offset)

    def set_encoding(self, data_to_encode):
        bits_to_store = len(data_to_encode) * 8
        byte_index = 0
        step = max(len(self.images) // Transcriber.POOL_SIZE, 1)
        extra = 0
        print("Encoding: ", bits_to_store)
        
        processes = []
        args = []
        while bits_to_store > 0:
            image_can_store = self.current_image.bits_that_can_store()
            if bits_to_store > image_can_store:
                print("\nstoring full", self.current_image, self.current_image.image_number, image_can_store, self.current_image.bit_length_to_store)
                temp = (self.current_image.source_image_path, self.current_image.destination_image_path, self.current_image.mode,
                    self.current_image.bit_length_to_store, self.current_image.image_number, len(self.images), data_to_encode, byte_index, self.leftover)
                args.append(temp)
                if len(args) % step == 0:
                    p = Process(target=Transcriber.do_parallel_images, args=args)
                    p.start()
                    processes.append(p)
                    args = []

                self.leftover = ((8 - (self.current_image.bit_length_to_store) % 8) + self.leftover) % 8
                extra += (self.current_image.bit_length_to_store) % 8
                byte_index += extra // 8
                extra = extra % 8

                # udpate lengths
                bits_to_store -= image_can_store
                self.total_bit_length -= image_can_store
                byte_index += image_can_store // 8

                # iterate current image
                self.current_image_index += 1
                self.current_image.close_image()
                self.current_image = self.images[self.current_image_index]
                image_can_store = self.current_image.bits_that_can_store()
                self.current_image.init_encoding(min(image_can_store, self.total_bit_length), self.current_image_index)
            else:
                if len(args) > 0:
                    p = Process(target=Transcriber.do_parallel_images, args=args)
                    p.start()
                    processes.append(p)
                    args = []

                print("storing partial", self.current_image, self.current_image.image_number, bits_to_store, self.leftover)
                self.leftover = self.current_image.encode_data(data_to_encode, byte_index, self.leftover)
                self.total_bit_length -= bits_to_store
                bits_to_store = 0
        
        for p in processes:
            p.join()
    def finish_encoding(self):
        self.current_image.finish_encoding()

