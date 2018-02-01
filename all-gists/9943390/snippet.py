#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import re

# dado um título e lista de listas no formato
# ('<variável>', '<tipo>', '<descricao>', '<fórmula>')
# pede-se qual variável calcular, pede os valores e dá o resultado
# qualquer valor vazio saida da função
def calcular(titulo, variaveis):
    # fazendo com que cada elemento da lista seja:
    # 0. lista de nomes das variáveis
    # 1. lista de descrições das variáveis
    # 2. lista de funções para calcular as variáveis
    variaveis_zip = zip(*variaveis)

    mascara = "%%%is(%%s): %%s => %%s" % max(map(len, variaveis_zip[0]))
    formato = {'v': '.3f', '%': '.3f%%', 'i': 'i'}

    print ('\nExplicação do conteúdo entre parênteses:\n'
           '(v) => valor com 3 casas decimais\n'
           '(%) => percentual com 3 casas decimais\n'
           '(i) => valor inteiro')

    while True:
        # mostrar o título e cada variável, com sua descrição e fórmula
        print '\n%s\n' % titulo
        for i in range(len(variaveis)):
            print mascara % variaveis[i]

        # pegunta pela variável a ser calculada
        calcular = ' '
        while calcular not in variaveis_zip[0]:
            calcular = raw_input("\nVariável que deseja calcular: ")
            if not calcular:
                return

        # fórmula da variável a calcular e sua formatação de resultado
        pos = variaveis_zip[0].index(calcular)
        f = variaveis_zip[3][pos]
        fmt = "%%s = %%%s" % formato[variaveis_zip[1][pos]]

        # variáveis da fórmula sem as funções de math.xxxxx
        f2 = re.sub(r'math\.\w+', '', f)
        vf = [i for i in set(re.findall(r'\w+', f2)) if not i.isdigit()
                                                      and i != calcular]

        # pegunta pelo valor das variáveis e troca na função em f2
        f2 = f
        for i in vf:
            # pergunta o valor de uma variável
            v = raw_input('Digite o valor de %s: ' % i).replace(',', '.')
            # sair se não digitar nada
            if not v:
                return
            # se tiver % no valor, tira ele e faz '/100.' entre parênteses
            if '%' in v:
                v = '(%s/100.)' % v.replace('%', '')
            # se não tiver '.' no valor, adiciona '.' para ser float
            elif '.' not in v:
                v += '.'
            # troca a variável pelo valor na fórmula
            f2 = re.sub(r'\b%s\b' % i, v, f2)
        if '=' in f2:
            # calcula via métodos numéricos
            resultado = calcular_numericamente_bisseccao(calcular, f2)
        else:
            # calcula a fórmula onde foram trocados os valores acima
            resultado = eval(f2.replace('^', '**'))

        # mostra o resultado
        print "\n%s: %s" % (calcular, f)
        print "%s: %s" % (calcular, f2)
        resultado *= 100. if variaveis[pos][1] == '%' else 1.
        print fmt % (calcular, resultado)

# calcular numericamente uma função crescente
def calcular_numericamente_bisseccao(i, f):
    f1, f2 = f.split('=')
    try:
        r = float(f1)
        f = f2.replace('^', '**')
    except ValueError:
        r = float(f2)
        f = f1.replace('^', '**')
    v = 0
    while True:
        try:
            c = eval(re.sub(r'\b%s\b' % i, str(v), f)) # calculado
            break
        except ZeroDivisionError:
            v += 1
    vmin = -1e10 - 1
    vmax = 1e10
    while abs(r - c) > 0.00001: # até 5 casas decimais de precisão
        if c > r:
            vmax = v
        else:
            vmin = v
        v = (vmin + vmax) / 2.
        c = eval(re.sub(r'\b%s\b' % i, str(v), f))
    return v

########################################################################

calcular('Juros simples', (
    ('S' , 'v', 'Valor futuro', 'P * (1 + i * n)'),
    ('P' , 'v', 'Valor presente', 'S / (1 + i * n)'),
    ('J' , 'v', 'Valor dos juros em valor', 'P * i * n'),
    ('J2', 'v', 'Valor dos juros em valor', 'S - P'),
    ('j' , '%', 'Juros final ou custo efetivo', 'i * n'),
    ('j2', '%', 'Juros final ou custo efetivo', '(S - P) / P'),
    ('i' , '%', 'Taxa por período', '(S / P - 1) / n'),
    ('n' , 'i', 'Número de períodos', '(S / P - 1) / i'),
))

calcular('Juros compostos', (
    ('S' , 'v', 'Valor futuro', 'P * (1 + i) ^ n'),
    ('P' , 'v', 'Valor presente', 'S / (1 + i) ^ n'),
    ('J' , 'v', 'Valor dos juros em valor', 'P * ((1 + i) ^ n - 1)'),
    ('J2', 'v', 'Valor dos juros em valor', 'S - P'),
    ('j' , '%', 'Juros final ou custo efetivo', '(1 + i) ^ n - 1'),
    ('j2', '%', 'Juros final ou custo efetivo', '(S - P) / P'),
    ('i' , '%', 'Taxa por período', '(S / P) ^ (1 / n) - 1'),
    ('n' , 'i', 'Número de períodos', 'math.log(S / P) / math.log(1 + i)'),
))

calcular('Amortização em parcelas iguais sem entrada', (
    ('R' , 'v', 'Valor da parcela', 'P * i * (1 + i) ^ n / ((1 + i) ^ n -1)'),
    ('S' , 'v', 'Valor futuro', 'R * ((1 + i) ^ n - 1) / i'),
    ('P' , 'v', 'Valor presente', 'R * ((1 + i) ^ n - 1) / (i * (1 + i) ^ n)'),
    ('j' , '%', 'Juro ou custo efetivo total', '(n * R - P) / P'),
    ('i' , '%', 'Taxa por perído - chuta-se uma até chegar em R', 'R = P * i * (1 + i) ^ n / ((1 + i) ^ n -1)'),
    ('n' , 'i', 'Número de parcelas', 'math.log(1 / (1 - i * P / R)) / math.log(1 + i)'),
))

calcular('Amortização em parcelas iguais com entrada', (
    ('R' , 'v', 'Valor da parcela', 'P * i * (1 + i) ^ (n - 1) / ((1 + i) ^ n -1)'),
    ('n' , 'i', 'Número de parcelas incluindo a entrada', 'n'),
))
