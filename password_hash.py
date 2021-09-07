import hashlib
import os

def password(args):

    salt_key = "saltedpassword"
    salt = hashlib.sha256(salt_key.encode()).hexdigest()
    key = hashlib.pbkdf2_hmac('sha256', args.password.encode('utf-8'), salt.encode('utf-8'), 100000)

    # Store them as:
    storage = salt + str(key)

    # Getting the values back out
    key_from_storage = storage[32:]

    return key_from_storage