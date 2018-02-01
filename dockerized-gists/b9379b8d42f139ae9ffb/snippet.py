from decimal import Decimal
from math import floor


def parcelas(valor, n, div=False, primeira=False):
    formato = Decimal('0.00')
    valor = Decimal(valor)
    if div:
        parcela = Decimal(floor(valor * 100 / n) / 100)
    else:
        parcela = Decimal(floor(valor / n))
    parcela = parcela.quantize(formato)
    if parcela * n < valor:
        parcelas = [parcela] * (n - 1)
        parcelas.append((valor - sum(parcelas)).quantize(formato))
        if primeira:
            parcelas[0], parcelas[-1] = parcelas[-1], parcelas[0]
    else:
        parcelas = [parcela] * n
    return parcelas


def main():
    for n in xrange(2, 11):
        print n,
        valor = Decimal('1593.00')
        for _ in xrange(0, 9001):
            for div in [True, False]:
                for pr in [True, False]:
                    ps = parcelas(valor, n, div, pr)
                    if sum(ps) != valor:
                        raise Exception('Erro: sum(%s) != %s, %s %s' % (ps, valor, div, pr))
            valor += Decimal('0.03')

if __name__ == '__main__':
    main()
