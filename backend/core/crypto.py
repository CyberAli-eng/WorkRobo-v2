from functools import lru_cache
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    key = getattr(settings, "CREDENTIALS_ENCRYPTION_KEY", None)
    if not key:
        raise RuntimeError("CREDENTIALS_ENCRYPTION_KEY is not set in Django settings.")
    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt(plaintext: str) -> str:
    """Symmetrically encrypts a plaintext string into a Fernet base64 ciphertext token."""
    if not plaintext:
        return ""
    return _fernet().encrypt(plaintext.encode()).decode()

def decrypt(token: str) -> str:
    """Decrypts a base64 ciphertext token back into a plaintext string."""
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as e:
        raise ValueError("Decryption failed: Cryptographic token is invalid or corrupted.") from e