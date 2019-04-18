import hashlib
def md5(str):
    return hashlib.md5(str.encode('utf-8')).hexdigest()

