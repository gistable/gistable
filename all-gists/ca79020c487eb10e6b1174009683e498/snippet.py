from __future__ import division  # para compatibilidade para divisão inteira // entre Python 2 e 3

import pprint
import timeit
from collections import deque


def somar_digitos_v1(number, base=10):
    assert number >= 0
    if number == 0:
        return deque([0])
    d = deque()
    while number > 0:
        # adiciona a esquerda
        d.appendleft(number % base)
        number = number // base
    return sum(d)


def somar_digitos_v2(numero):
    lista = []
    numero_em_str = str(numero)
    for letra in numero_em_str:
        numero = int(letra)
        # insere no inicio da lista (ps, isso eh ineficiente)
        lista.insert(0, numero)
    soma = 0
    for numero in lista:
        soma = soma + numero
    return soma


def somar_digitos_v3(numero):
    soma = 0
    numero_em_str = str(numero)
    for letra in numero_em_str:
        soma = soma + int(letra)
    return soma


def somar_digitos_v4(numero):  # usando list comprehension
    return sum([int(letra) for letra in str(numero)])


def somar_digitos_v5(numero):  # usango generator expression
    return sum((int(letra) for letra in str(numero)))


def somar_digitos_v6(numero):
   r = 0
   while numero:
       r, numero = r + numero % 10, numero // 10
   return r

# Testes
def test_soma_v1():
    return somar_digitos_v1(53525150593564)


def test_soma_v2():
    return somar_digitos_v2(53525150593564)


def test_soma_v3():
    return somar_digitos_v3(53525150593564)


def test_soma_v4():
    return somar_digitos_v4(53525150593564)


def test_soma_v5():
    return somar_digitos_v5(53525150593564)


def test_soma_v6():
    return somar_digitos_v6(53525150593564)

# funcao python tambem sao objetos, entao voce pode coloca-las numa lista :-)
funcoes = [test_soma_v1, test_soma_v2, test_soma_v3, test_soma_v4, test_soma_v5, test_soma_v6]



resultado = {funcao.__name__: {'tempo': timeit.Timer(funcao).timeit(), 'retorno': funcao()} for funcao in funcoes}



pprint.pprint(resultado)
