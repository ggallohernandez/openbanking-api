import hashlib
import json

def dict_hash(dictionary):
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()

def get_checksum(item):
    """Get a checksum of the item."""
    return hashlib.md5(str(item.__hash__()).encode("utf8")).hexdigest()

def get_string_checksum(s):
    """Get a checksum of the item."""
    return hashlib.md5(s.encode("utf8")).hexdigest()