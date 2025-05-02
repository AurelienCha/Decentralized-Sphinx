import hashlib
import datetime
import secrets
import random
import inspect

from param import COUNT_OPERATIONS
operation_log = []

def track_operation(func): # Decorator
    def wrapper(*args, **kwargs):
        if COUNT_OPERATIONS: # Save stack
            for (op, file, fct) in [(func.__name__, f.filename.split('/')[-1], f.function) for f in inspect.stack()[1:-1]]:
                if file in ['client.py', 'mixnode.py', 'ttp.py', 'setup.py', 'elligator.py']:
                    operation_log.append((op, file, fct))
                    break
        return func(*args, **kwargs)
    return wrapper

def extract_operation_log():
    global operation_log
    log, operation_log = operation_log, []
    return log

def truncated_hash(bytes_: bytes, it: int = 1, bits: int = 255) -> int:
    """
    Implementation of a truncated SHA-256 hash with an option for multiple iterations (i.e. hash(hash(...)))

    Args:
        bytes_ (bytes): The input data to hash
        it (int, optional): Number of hash iterations := Defaults to 1
        bits (int, optional): Output bit size (≤ 256) := Defaults to 255
    """

    def _hash(bytes_, iterations):
        if iterations > 1:
            bytes_ = _hash(bytes_, iterations-1)
        return hashlib.sha256(bytes_).digest()

    if not isinstance(bytes_, bytes):
        raise TypeError(f"Error: hash() takes bytes object")
    if bits > 256:
        raise ValueError(f"Error: maximum hash size is 256 bits (you asked for {bits} bits)")
    return int.from_bytes(_hash(bytes_, it)) >> (256-bits)
    
def rnd_padding(ip: int, pad_size: int = 124) -> int:
    """
    Prepend an IP integer (128 bits) with a random padding (default 124 bits for the padding)

    Args:
        ip (int): IP address as a 128-bit integer
        pad_size (int, optional): Number of random bits to prepend (Defaults to 124)

    NOTE: Output must be smaller than N (252-bit) therefore the padding must be 124-bit (124 + 128 = 252)
    """
    padding = bin(secrets.randbits(pad_size))[2:].zfill(pad_size)
    return int(padding + f"{ip:0128b}", 2)

def random_ip() -> int:
    """
    Return a simulated random IPv6 address (128-bit)
    """
    return random.randint(1,pow(2,128)) 
