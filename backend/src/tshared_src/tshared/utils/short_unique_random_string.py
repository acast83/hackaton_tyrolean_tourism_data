import string
import random
import secrets


alphabet = string.ascii_lowercase + string.digits


def get_short_unique_random_string(length: int):
    # return secrets.token_hex(length // 2)
    # return ''.join(secrets.choice(alphabet) for _ in range(length))
    return ''.join(random.choices(alphabet, k=length))
