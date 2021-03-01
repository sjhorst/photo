def sha1_hash(filename):
    import hashlib

    hash_sha1 = hashlib.sha1()
    with open(filename, 'rb') as fid:
        for chunk in iter(lambda: fid.read(4096), b""):
            hash_sha1.update(chunk)

    return hash_sha1.hexdigest()
