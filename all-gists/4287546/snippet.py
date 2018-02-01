# FROM:  http://en.wikipedia.org/wiki/Base_36#Python_implementation
def base36encode(number):
    """Converts an integer into a base36 string."""

    ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if not isinstance(number, (int, long)):
        raise TypeError('This function must be called on an integer.')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(ALPHABET):
        return sign + ALPHABET[number]

    while number != 0:
        number, i = divmod(number, len(ALPHABET))
        base36 = ALPHABET[i] + base36

    return sign + base36


def base36decode(number):
    return int(number, 36)