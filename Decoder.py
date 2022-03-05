from Encryption import Encryption as GCM
from Extractor import Extractor
from Transcriber import Transcriber


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

    def get_length_field_length(self):
        return Transcriber.bytes_for_size((self.extractor.get_total_pixels() * 2) // 8)

    def get_header_length(self):
        return Decoder.MODE_LENGTH + GCM.get_iv_length() + GCM.get_salt_length() + self.get_length_field_length()

    def decode_header(self, raw_header):
        # assume raw_header is bytearray of values
        self.mode = raw_header[0]
        salt_end = GCM.get_salt_length() + 1
        gcm_end = salt_end + GCM.get_iv_length()
        password_salt = bytes(raw_header[1: salt_end])
        iv = bytes(raw_header[salt_end: gcm_end])

        self._gcm = GCM(iv=iv, password_salt=password_salt)
        self._gcm.make_key(self._password)
        del self._password

        self._data_length = int.from_bytes(bytes(raw_header[gcm_end: gcm_end + self.get_length_field_length()]),
                                           byteorder='big', signed=False)

    def decode_file(self, file_path):

        self.extractor.load_images()
        # raw_header = self.extractor.decode_image(self.get_header_length())
        # self.decode_header(raw_header)

        # print(self.mode)
        # print(self._data_length)



if __name__ == "__main__":
    enc = Decoder(b'password', 'destination_images')
    enc.decode_file('input.txt')
