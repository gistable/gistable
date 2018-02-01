# encoding=utf-8

# Obtener el dígito verificador del RUT en Python.
#
# La función recibe el RUT como un entero,
# y entrega el dígito verificador como un entero.
# Si el resultado es 10, el RUT es "raya k".

from itertools import cycle

def digito_verificador(rut):
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    return (-s) % 11
