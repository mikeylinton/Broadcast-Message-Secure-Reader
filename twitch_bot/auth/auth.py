import datetime
import random
import string



def get_random_string(_len: int = 32):
    return "".join(random.sample(string.ascii_letters + string.digits, _len))


def is_expired(_datetime: str) -> bool:
    try:
        expires_on = datetime.datetime.strptime(_datetime, "%Y-%m-%d %H:%M:%S.%f")
        expired = datetime.datetime.now() > expires_on
    except ValueError:
        return True
    return expired
