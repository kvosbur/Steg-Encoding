import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encryption:

    def __init__(self, iv=None, password_salt=None, tag=None):
        self.iv = iv or os.urandom(12)
        self.password_salt = password_salt or os.urandom(16)
        self._tag = tag
        self._cipher = None
        self._key = None
        self._encryptor = None
        self._decryptor = None

    def create_cipher(self):
        if self._key is None:
            raise Exception('Key has yet to be made')
        if self._tag is not None:
            self._cipher = Cipher(algorithms.AES(self._key), modes.GCM(self.iv, self._tag))
        else:
            self._cipher = Cipher(algorithms.AES(self._key), modes.GCM(self.iv))

    def make_key(self, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.password_salt,
            iterations=100000
        )
        self._key = kdf.derive(password)

    def encrypt(self, pt):
        if self._cipher is None:
            self.create_cipher()
            self._encryptor = self._cipher.encryptor()

        return self._encryptor.update(pt)

    def encrypt_finalize(self):
        self._encryptor.finalize()
        return self._encryptor.tag

    def decrypt(self, ct):
        if self._cipher is None:
            if self._tag is None:
                raise Exception('Class must be intstantiated with tag if decrypting')
            self.create_cipher()
            self._decryptor = self._cipher.decryptor()

        return self._decryptor.update(ct)

    def decrypt_finalize(self):
        self._decryptor.finalize()


if __name__ == "__main":
    given_password = b'super secure password'
    plaintext = b'super secure message'
    print(plaintext)
    e = Encryption()
    e.make_key(given_password)
    ct = e.encrypt(plaintext)
    t = e.encrypt_finalize()

    d = Encryption(iv=e.iv, password_salt=e.password_salt, tag=t)
    d.make_key(given_password)
    actual = d.decrypt(ct)
    d.decrypt_finalize()
    print(actual)
