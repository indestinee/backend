import hashlib
import hmac


def hmac_sha256(key: bytes, value: bytes) -> bytes:
    sha256 = hmac.new(key, value, hashlib.sha256)
    return sha256.digest()
