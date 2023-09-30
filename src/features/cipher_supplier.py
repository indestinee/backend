import json
import os

from Crypto.Cipher import AES

from src.config import CipherConfig
from src.data.cipher import Cipher
from src.utils.hash_utils import hmac_sha256


class CipherSupplier:
    def decrypt(self, key: str, cipher: str) -> bytes:
        cipher = Cipher(**json.loads(cipher))
        salt = bytes.fromhex(cipher.salt)
        aes_key = self.generate_cipher(key, "aes_key", salt)
        aes_iv = self.generate_cipher(key, "aes_iv", salt)[:16]
        aes = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
        augmented_text = aes.decrypt(bytes.fromhex(cipher.cipher_text))
        return bytes.fromhex(augmented_text.hex()[::2])[: cipher.text_length]

    def encrypt(self, key: str, text: bytes) -> Cipher:
        augmented_text = self.augment_bytes(text, CipherConfig.cipher_size)
        salt = os.urandom(CipherConfig.salt_size)

        aes_key = self.generate_cipher(key, "aes_key", salt)
        aes_iv = self.generate_cipher(key, "aes_iv", salt)[:16]

        aes = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
        cipher_text = aes.encrypt(augmented_text)

        return Cipher(
            cipher_text=cipher_text.hex(),
            text_length=len(text),
            salt=salt.hex(),
        )

    @staticmethod
    def generate_cipher(key: str, name: str, salt: bytes) -> bytes:
        return hmac_sha256(
            hmac_sha256(key.encode("utf-8"), name.encode("utf-8")),
            salt,
        )

    @staticmethod
    def augment_bytes(data: bytes, padding_size: int) -> bytes:
        padded_text = (data + os.urandom(padding_size - len(data) % padding_size)).hex()
        random_bytes = os.urandom(len(padded_text)).hex()
        mixture = bytes.fromhex("".join(map("".join, zip(padded_text, random_bytes))))
        return mixture

    @staticmethod
    def de_augment_bytes(data: bytes, length: int) -> bytes:
        return bytes.fromhex(data.hex()[::2])[:length]
