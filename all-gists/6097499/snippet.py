import math
import decimal

def convert_to_code(num):
    """
    将数字转换为代码
    """
    def get_num(num, out=''):
        num = decimal.Decimal(num)
        codes = "abcdefghjkmnpqrstuvwxyz23456789ABCDEFGHJKMNPQRSTUVWXYZ"
        if num > 53:
            key = num % 54
            num = math.floor(num / 54) - 1
            return get_num(num, codes[int(key)] + out)
        else:
            return codes[int(num)] + out
    return get_num(num)


def convert_to_num(code):
    """
    将代码转为数字
    """
    import math
    codes = "abcdefghjkmnpqrstuvwxyz23456789ABCDEFGHJKMNPQRSTUVWXYZ"
    num = 0
    num = decimal.Decimal(num)
    i = len(code)
    for char in code:
        i -= 1
        pos = codes.find(char)
        num += (54 ** i) * (pos + 1)
    num -= 1
    # 任意数的 0 次方等于1，所以需要减去
    return int(num)
