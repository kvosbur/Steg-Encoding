from Encryption import Encryption as GCM
from Transcriber import Transcriber
import shutil
import os
import datetime
import cProfile
import pstats
from pstats import SortKey


class Encoder:

    MODES = {'GCM': 8}

    def __init__(self, password, source_image_folder_path, destination_image_folder_path, mode='GCM'):
        self.mode = Encoder.MODES[mode]
        self.source_image_folder_path = source_image_folder_path
        self.destination_image_folder_path = destination_image_folder_path
        if os.path.exists(self.destination_image_folder_path):
            shutil.rmtree(self.destination_image_folder_path)
        os.makedirs(self.destination_image_folder_path)

        self.gcm = GCM()
        self.gcm.make_key(password)
        self.transcriber = Transcriber(self.mode, source_image_folder_path, destination_image_folder_path)

    def encode_file(self, file_path):
        with open(file_path, 'rb') as source:
            file_bytes = source.read()
            encrypted = self.gcm.encrypt(file_bytes)
            tag = self.gcm.encrypt_finalize()

        header = self.gcm.password_salt + self.gcm.iv

        full_length = len(header) + len(encrypted) + len(tag)
        if not self.transcriber.can_fit_bytes(full_length):
            print("Not enough images to store the necessary data")
            exit()

        print("full length", full_length, full_length * 8)

        self.transcriber.set_encoding(header + encrypted + tag)
        with open("encode-test", "wb") as f:
            f.write(header + encrypted + tag)
        # self.transcriber.set_encoding(encrypted)
        # self.transcriber.set_encoding(tag)
        self.transcriber.finish_encoding()

if __name__ == "__main__":
    before = datetime.datetime.now()
    enc = Encoder(b'password', './source_images', './destination_images')
    # profile_result_file = "results"
    # print("Running profiler")
    # cProfile.run("enc.encode_file('source_images.zip')", profile_result_file)

    # p = pstats.Stats(profile_result_file)
    # p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()

    enc.encode_file('./large.txt')

    after = datetime.datetime.now()
    total = after - before
    print(f"total time taken: {total}")
