from hashlib import sha256
from datetime import date

def _hash(bytes_, iterations):
    if iterations > 1:
        bytes_ = _hash(bytes_, iterations-1)
    return sha256(bytes_).digest()
    
def hash(bytes_, it=1, bits=256):
    if not isinstance(bytes_, bytes):
        raise TypeError(f"Error: hash() takes bytes object")
    if bits > 256:
        raise ValueError(f"Error: maximum hash size is 256 bits (you asked for {bits} bits)")
    return int.from_bytes(_hash(bytes_, it)) >> (256-bits)