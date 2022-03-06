from Encryption import Encryption as GCM
from Extractor import Extractor
import cProfile
import pstats
from pstats import SortKey
import datetime


class Decoder:

    MODES = {'GCM': 8}
    MODE_LENGTH = 1

    def __init__(self, password, image_folder_path):
        self.image_folder_path = image_folder_path
        self.mode = None
        self._gcm = None
        self._password = password
        self._data_length = 0

        self.extractor = Extractor(image_folder_path)

    def get_header_length(self):
        return GCM.get_iv_length() + GCM.get_salt_length()

    def decode_header(self, raw_header):
        # assume raw_header is bytearray of values
        salt_end = GCM.get_salt_length()
        gcm_end = salt_end + GCM.get_iv_length()
        password_salt = bytes(raw_header[: salt_end])
        iv = bytes(raw_header[salt_end: gcm_end])

        self._gcm = GCM(iv=iv, password_salt=password_salt)
        self._gcm.make_key(self._password)
        del self._password

    def get_tag(self, raw_data):
        tag = bytes(raw_data[-GCM.get_tag_length():])
        self._gcm.set_tag(tag)

    def decrypt_and_save_data(self, raw_data, destination_file):
        decrypted = self._gcm.decrypt(raw_data[self.get_header_length(): -GCM.get_tag_length()])
        # with open("temp", "wb") as f:
        #     f.write(decrypted)
        self._gcm.decrypt_finalize()

        with open(destination_file, "wb") as f:
            f.write(decrypted)


    def decode_file(self, file_path):

        raw_data = self.extractor.load_images()
        # with open("decode-test", "wb") as f:
        #     f.write(raw_data)

        raw_header = raw_data[:self.get_header_length()]
        self.decode_header(raw_header)
        self.get_tag(raw_data)

        self.decrypt_and_save_data(raw_data, file_path)


if __name__ == "__main__":
    before = datetime.datetime.now()
    enc = Decoder(b'password', 'destination_images')
    # profile_result_file = "results"
    # print("Running profiler")
    # cProfile.run("enc.decode_file('output')", profile_result_file)

    # p = pstats.Stats(profile_result_file)
    # p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()

    enc.decode_file('output')

    after = datetime.datetime.now()
    total = after - before
    print(f"total time taken: {total}")
    
