import copy
import typing


def normalize_phone_number(s):
    for allowed_char_to_remove in '() ./-_':
        s = s.replace(allowed_char_to_remove, '')
    return s


def is_phone_number(s):
    if type(s) == int:
        s = str(s)

    if type(s) != str:
        return False

    s = normalize_phone_number(s)

    try:
        int(s)
    except:
        return False

    return len(s) > 3


def strip_html_special(value):
    val = copy.copy(value)
    if val and type(val) == str:

        for k, v in (("&lt;", "<"),
                     ("&gt;", ">"),
                     ("&amp;", "&"),
                     ):
            val = val.replace(k, v)
    return val


class IsPortFromReservedRange:
    def __init__(self):
        # https://www.rfc-editor.org/rfc/rfc1700.html
        """
        https://www.rfc-editor.org/rfc/rfc6335.html
        6. Port Number Ranges

        Well Known Ports: 0 through 1023.
        Registered Ports: 1024 through 49151.
        Dynamic/Private : 49152 through 65535.
        o  the System Ports, also known as the Well Known Ports, from
           0-1023 (assigned by IANA)
        o  the User Ports, also known as the Registered Ports, from
           1024-49151 (assigned by IANA)
        o  the Dynamic Ports, also known as the Private or Ephemeral Ports, from
           49152-65535 (never assigned)
        """

        self.MIN_PORT = 1024
        self.MAX_PORT = 49151

        # https://www.rfc-editor.org/rfc/rfc1700.html
        rfc_reserved_ranges = (
            "1024-1025", "1030-1032", "1067-1068", "1080-1080", "1083-1084", "1155-1155",
            "1222-1222", "1248-1248", "1346-1505", "1506-1523", "1524-1527", "1529-1529",
            "1600-1600", "1650-1655", "1661-1666", "1986-2002", "2004-2028", "2030-2030",
            "2032-2035", "2038-2038", "2040-2049", "2065-2065", "2067-2067", "2201-2201",
            "2500-2501", "2564-2564", "2784-2784", "3049-3049", "3264-3264", "3333-3333",
            "3984-3986", "4132-4133", "4343-4343", "4444-4444", "4672-4672", "5000-5002",
            "5010-5011", "5050-5050", "5145-5145", "5190-5190", "5236-5236", "5300-5305",
            "6000-6063", "6000-6063", "6111-6111", "6141-6147", "6558-6558", "7000-7010",
            "7100-7100", "7200-7200", "9535-9535"
        )
        self.ranges = [self._range(*[int(port) for port in x.split('-')])
                       for x in rfc_reserved_ranges]

    def __call__(self, port) -> bool:
        port = int(port)

        if self.MIN_PORT > port or port > self.MAX_PORT:
            return True

        for r in self.ranges:
            if port in r:
                return True
        return False

    @staticmethod
    def _range(start, stop):
        return range(start, stop + 1)


is_port_from_reserved_range = IsPortFromReservedRange()


def suggest_port(port, min_port: int = 1024, max_port: int = 49151) -> typing.Optional[int]:

    port = max(int(port), min_port)

    if port and is_port_from_reserved_range(port):
        for p in range(port, max_port + 1):
            if not is_port_from_reserved_range(p):
                return p
        return None
    else:
        return port


if __name__ == "__main__":
    for p in range(1024, 49151 + 1):
        print(is_port_from_reserved_range(p), end=' ')
