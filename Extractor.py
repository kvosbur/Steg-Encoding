from os import path, listdir, mkdir
from ExtractImage import ExtractImage
from multiprocessing import Process
import shutil


def overwrite_pixel_value(prev_value, value_to_hide):
    return (prev_value & 252) | value_to_hide


class Extractor:

    POOL_SIZE = 6

    def __init__(self, image_folder):
        self.data_folder_path = "./tempData"
        if path.exists(self.data_folder_path):
            shutil.rmtree(self.data_folder_path)
        mkdir(self.data_folder_path)
        if not path.exists(image_folder):
            raise Exception("Image path is incorrect or does not exist!")
        self.image_folder = image_folder

    def gather_data(self): 
        sorted_files = sorted([int(x) for x in listdir(self.data_folder_path)])
        print(sorted_files)

        data = bytearray()
        for file in sorted_files:
            file_path = path.join(self.data_folder_path, str(file))
            with open(file_path, "rb") as f:
                data += f.read()

        return data

    @staticmethod
    def do_parallel_images_load(*args):
        for (image_path, offset, val, data_folder_path) in args:
            image = ExtractImage(path.join(image_path))
            image.get_header()
            image.offset = offset
            image.val = val
            data = image.decode_image()

            data_path = path.join(data_folder_path, str(image.image_number))
            print("wrote data for:", data_path)
            with open(data_path, "wb") as f:
                f.write(data)

    def load_images(self):
        self.images = [ExtractImage(path.join(self.image_folder, image)) for image in listdir(self.image_folder)]
        [image.get_header() for image in self.images]
        sorted_images = sorted(self.images, key=lambda image: image.image_number)
        import pprint
        pprint.pprint(sorted_images)

        prev_offset = 0
        prev_val = 0
        processes = []
        args = []
        step = max(len(self.images) // Extractor.POOL_SIZE, 1)
        for index, image in enumerate(sorted_images):
            temp = (image.image_path, prev_offset, prev_val, self.data_folder_path)
            args.append(temp)
            if len(args) % step == 0:
                p = Process(target=Extractor.do_parallel_images_load, args=args)
                p.start()
                processes.append(p)
                args = []
            # image.offset = prev_offset
            # image.val = prev_val
            prev_offset, prev_val = image.get_final_offset(prev_offset)
            # data += image.decode_image()
            # prev_offset = image.offset
            # prev_val = image.val
            
            # print(image, image.bits_read, prev_val, prev_offset, "{0:.0%}".format(index / len(sorted_images)))
            # print("predicted", predict_off, predict_val)
            # print("")

        if len(args) > 0:
            p = Process(target=Extractor.do_parallel_images_load, args=args)
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        return self.gather_data()
