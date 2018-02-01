def decomp(num):
    """decomp(120) == (100, 20)"""
    base = 10 ** (len(str(num))-1)
    divisor, resto = divmod(num, base)
    return divisor * base, resto

  
def radicais(resto):
    while resto > 0:
        base, resto = decomp(resto)
        yield base

        
def extenso(num):
    d = {
        1: 'um', 2: 'dois', 3: 'três', 4: 'quatro', 5: 'cinco', 
        6: 'seis', 7: 'sete', 8: 'oito', 9: 'nove',
        10: 'dez', 11: 'onze', 12: 'doze', 13: 'treze', 14: 'quatorze', 15: 'quinze', 
        16: 'dezesseis', 17: 'dezessete', 18: 'dezoito', 19: 'dezenove',
        20: 'vinte', 30: 'trinta', 40: 'quarenta', 50: 'cinquenta', 
        60: 'sessenta', 70: 'setenta', 80: 'oitenta', 90: 'noventa',
        100: 'cento'
    }
    
    if num == 100:
        return 'cem'
    elif num == 0:
        return 'zero'

    return ' e '.join((d[r] for r in radicais(num)))    


if __name__ == '__main__':
    assert decomp(120) == (100, 20)
    assert decomp(121) == (100, 21)

    assert list(radicais(120)) == [100, 20]
    assert list(radicais(121)) == [100, 20, 1]

    assert extenso(0) == 'zero'
    assert extenso(1) == 'um'
    assert extenso(2) == 'dois'
    assert extenso(10) == 'dez'
    assert extenso(20) == 'vinte'
    assert extenso(21) == 'vinte e um'
    assert extenso(29) == 'vinte e nove'
    assert extenso(30) == 'trinta'
    assert extenso(31) == 'trinta e um'
    assert extenso(40) == 'quarenta'
    assert extenso(41) == 'quarenta e um'
    assert extenso(100) == 'cem'
    assert extenso(101) == 'cento e um'
    assert extenso(120) == 'cento e vinte'
    assert extenso(121) == 'cento e vinte e um'
