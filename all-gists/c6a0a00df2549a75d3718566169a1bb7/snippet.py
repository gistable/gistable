import operator
def check_erdpou(code):
    """ Алгоритм проверки кода ЕРДПОУ """
    code = int(code)

    def check(sec, shift=False, step=0):
        """ Генерация контрольного числа """
        nums = list(range(1 + step, 8 + step))
        if shift:
            nums.insert(0, nums.pop(6))
        return sum(map(operator.mul, sec, nums)) % 11

    icode = [int(i) for i in "{:0>8}".format(code)]
    shift = True
    if code < 30000000 or code > 60000000:
        shift = False
    val = check(icode, shift)
    if val < 10:
        return val == icode[-1]
    val = check(icode, shift, step=2)
    if val < 10:
        return val == icode[-1]
    return False

# for c in [13434579, 13434585, '32855961', '00000000', '00000001', '14312364']:
#     print(check_erdpou(c))