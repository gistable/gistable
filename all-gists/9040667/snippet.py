# coding: utf-8


def cpf_checksum(value):
    """
    CPF Checksum algorithm.
    """
    def dv(partial):
        s = sum(b * int(v) for b, v in zip(range(len(partial)+1, 1, -1), partial))
        return s % 11

    dv1 = 11 - dv(value[:9])
    q2 = dv(value[:10])
    dv2 = 11 - q2 if q2 >= 2 else 0

    return dv1 == int(value[9]) and dv2 == int(value[10])


def tests():
    assert cpf_checksum('11144477735') == True
    assert cpf_checksum('21111111120') == True
    assert cpf_checksum('00000000000') == False

tests()