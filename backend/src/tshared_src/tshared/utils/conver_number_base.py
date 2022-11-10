import uuid
import typing
import string


__all__ = [
    "atoi",
    "itoa",
    "compress_uuid_4",
    "uncompress_uuid_4"
    ]


DIGS = string.digits + string.ascii_letters
assert len(DIGS) == len(set(DIGS))

# alphabets for representing number of bases higher than 10
ALPHA_FORWARD = {k: v for k, v in zip(DIGS, range(len(DIGS)))}
ALPHA_BACKWARD = {k: v for k, v in zip(range(len(DIGS)), DIGS)}


def atoi(number: str, base: int = 10) -> int:
    number = number.strip()

    if 2 <= base <= 32:
        return int(number, base=base)
    elif 32 < base <= len(DIGS):
        sign = 1
        if number[0] == '-':
            sign = -1
            number = number[1:]
        if number[0] == '+':
            number = number[1:]

        result = 0
        for c in list(number):
            result = (result * base) + ALPHA_FORWARD[c]
        return result * sign
    else:
        raise ValueError(f'Unsupported base {base}.')


def itoa(number: int, base: int = 10) -> str:
    result = ''
    if 0 > number:
        result += '-'

    if 2 <= base <= len(DIGS):
        if number == 0:
            return '0'

        while number:
            result += ALPHA_BACKWARD[number % base]
            number //= base
        return result[::-1]
    else:
        raise ValueError(f'Unsupported base {base}.')


def compress_uuid_4(u: typing.Union[uuid.UUID, str], base: int = None) -> str:
    """compresses uuid from 32 characters to
    with base 32 (uses C api of python):
        max(26), min(22), avg(25)
    with base 62 (uses slow python loops):
        max(22), min(19), avg(21)
    """

    if base is None:
        base = len(DIGS)

    if isinstance(u, str):
        u = u.replace('-', '')
    elif isinstance(u, uuid.UUID):
        u = str(u).replace('-', '')
    else:
        raise ValueError(f'Unsupported type {type(u)}')

    result = atoi(u, base=16)
    return itoa(result, base=base)


def uncompress_uuid_4(u: str, base: int = None) -> uuid.UUID:
    if base is None:
        base = len(DIGS)

    result = atoi(u, base=base)
    q = itoa(result, base=16)
    q = '0' * (32 - len(q)) + q
    return uuid.UUID(q)


def check_bases():
    for base in range(2, len(DIGS) + 1):
        for num in range(1_000_000):
            s = itoa(number=num, base=base)
            i = atoi(number=s, base=base)
            try:
                assert num == i
            except Exception as e:
                print(num, s, i)


def check_compress():
    n = 100_000

    max_len = 0
    min_len = 35
    total_len = 0
    base = len(DIGS)

    try:
        for _ in range(n):
            num = uuid.uuid4()

            c = compress_uuid_4(num, base=base)
            total_len += len(c)
            max_len = max(max_len, len(c))
            min_len = min(min_len, len(c))
            u = uncompress_uuid_4(c, base=base)
            assert num == u
        print(f"base: {base}\n  max: {max_len}\n  min: {min_len}\n  avg: {total_len // n}")
    except ValueError as e:
        print("origin:", str(num).replace('-', ''))


if __name__ == "__main__":
    check_bases()
    check_compress()
