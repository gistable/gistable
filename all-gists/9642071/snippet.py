# http://snipperize.todayclose.com/snippet/py/64-%E5%92%8C-10%E8%BF%9B%E5%88%B6--93237/


def encode_b64(n):
    table = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
    result = []
    temp = n
    if 0 == temp:
    ¦   result.append('0')
    else:
    ¦   while 0 < temp:
    ¦   ¦   result.append(table[temp % 64])
    ¦   ¦   temp /= 64
    return ''.join([x for x in reversed(result)])


def decode_b64(str):
    table = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    ¦   ¦   ¦"6": 6, "7": 7, "8": 8, "9": 9,
    ¦   ¦   ¦"a": 10, "b": 11, "c": 12, "d": 13, "e": 14, "f": 15, "g": 16,
    ¦   ¦   ¦"h": 17, "i": 18, "j": 19, "k": 20, "l": 21, "m": 22, "n": 23,
    ¦   ¦   ¦"o": 24, "p": 25, "q": 26, "r": 27, "s": 28, "t": 29, "u": 30,
    ¦   ¦   ¦"v": 31, "w": 32, "x": 33, "y": 34, "z": 35,
    ¦   ¦   ¦"A": 36, "B": 37, "C": 38, "D": 39, "E": 40, "F": 41, "G": 42,
    ¦   ¦   ¦"H": 43, "I": 44, "J": 45, "K": 46, "L": 47, "M": 48, "N": 49,
    ¦   ¦   ¦"O": 50, "P": 51, "Q": 52, "R": 53, "S": 54, "T": 55, "U": 56,
    ¦   ¦   ¦"V": 57, "W": 58, "X": 59, "Y": 60, "Z": 61,
    ¦   ¦   ¦"-": 62, "_": 63}
    result = 0
    for i in xrange(len(str)):
    ¦   result *= 64
    ¦   result += table[str[i]]
    return result

a = "53219ebcbe238721a805d3fe"
a_int = int(a, 16)

print encode_b64(a_int)
