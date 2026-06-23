import base64

from Crypto import Random
from Crypto.Cipher import AES


class CipherTool:

    @staticmethod
    def aes_encrypt_pad(_str: str, bs: int = 16) -> str:
        return _str + (bs - len(_str.encode("utf-8")) % bs) * chr(bs - len(_str.encode("utf-8")) % bs)

    @staticmethod
    def aes_encrypt_unpad(_bytes: bytes) -> bytes:
        return _bytes[:-ord(_bytes[len(_bytes) - 1:])]

    @staticmethod
    def aes_encrypt_str(key: str, raw_str: str, bs: int = 16) -> str:
        return CipherTool.aes_encrypt(key=key.encode("utf-8"), raw_str=raw_str, bs=bs).decode("utf-8")

    @staticmethod
    def aes_encrypt(key: bytes, raw_str: str, bs: int = 16) -> bytes:
        raw = CipherTool.aes_encrypt_pad(raw_str, bs=bs)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode("utf-8")))

    @staticmethod
    def aes_decrypt_str(key: str, encrypt_str: str, bs: int = 16) -> str:
        return CipherTool.aes_decrypt(key=key.encode("utf-8"), encrypt_str=encrypt_str, bs=bs).decode("utf-8")

    @staticmethod
    def aes_decrypt(key: bytes, encrypt_str: str, bs: int = 16) -> bytes:
        encrypt_str = base64.b64decode(encrypt_str.encode("utf-8"))
        iv = encrypt_str[:bs]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return CipherTool.aes_encrypt_unpad(cipher.decrypt(encrypt_str[bs:]))
