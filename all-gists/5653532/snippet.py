# coding=UTF-8

"""
Faça um Programa que leia um número inteiro menor que 1000 
e imprima a quantidade de centenas, dezenas e unidades do mesmo.
Observando os termos no plural a colocação do "e", da vírgula entre outros. 

Exemplo:
326 = 3 centenas, 2 dezenas e 6 unidades
"""

number = int(raw_input("Digite um numero: "))

if number > 0 and number < 1000:
    centenas = number / 100
    dezenas = (number % 100) / 10
    unidades = (number % 100) % 10

    msg = list()
    msg.append("%s =" % number)

    if centenas == 1:
        msg.append("%s centena," % centenas)
    else:
        msg.append("%s centenas," % centenas)

    if dezenas == 1:
        msg.append("%s dezena e" % dezenas)
    else:
        msg.append("%s dezenas e" % dezenas)

    if unidades == 1:
        msg.append("%s unidade" % unidades)
    else:
        msg.append("%s unidades" % unidades)

    print ' '.join(msg)
else:
    print "Insira um numero maior que zero (0) ou menor que (1000)"