import uuid


alphabet = (
    '!"#$%&\'()*+,-./0123456789:;<=>?@'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '[\\]^_`'
    'abcdefghijklmnopqrstuvwxyz{|}~'
)


def uuid_compress(uuid):
    num = uuid.int
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def uuid_decompress(string):
    base = len(alphabet)
    strlen = len(string)
    num = 0
    for idx, char in enumerate(string):
        power = strlen - (idx + 1)
        num += alphabet.index(char) * (base ** power)
    return uuid.UUID(int=num)