# Autor: Leonardo Vinicius Maciel
# Exercícios de Pseudocódigo convertidos para python
# O Algoritmo está escrito de forma a ficar parecido com as regras de declaração e fluxo
# de pseudocódigo, por isso, muitas convenções do python foram quebradas, além de coisas
# desnecessárias, como por exemplo a declaração de variáveis e o print antes do input (a
# string pode ser passada diretamente como parametro do input). O código também
# representa apenas uma das inúmeras possibilidades de resolução.
import math


# Exercício 3
def calcula_distancia_pontos():
    p1x, p2x, p1y, p2y, dist = 0.0, 0.0, 0.0, 0.0, 0.0
    print("Informe a posição x do ponto 1")
    p1x = float(input())
    print("Informe a posição y do ponto 1")
    p1y = float(input())
    print("Informe a posição x do ponto 2")
    p2x = float(input())
    print("Informe a posição y do ponto 2")
    p2y = float(input())
    dist = math.sqrt((p2x - p1x)**2 + (p2y - p1y)**2)
    print("A distância entre ( " + str(p1x) + "," + str(p1y) + " ) e ( " + str(p2x) + "," + str(p2y) + " ) é de " + str(dist))


# Exercício 4
def calcula_formula():
    a, b, c, r, s = 0.0, 0.0, 0.0, 0.0, 0.0
    print("Informe o valor de a")
    a = int(input())
    print("Informe o valor de b")
    b = int(input())
    print("Informe o valor de c")
    c = int(input())
    r = (a + b)**2
    s = (b + c)**2
    print("r = " + str(r) + " e s = " + str(s))


# Exercício 5
def calcula_idade_anos_meses_dias():
    anos, meses, dias, total = 0, 0, 0, 0
    DIASMES = 30
    DIASANO = 365
    print("Informe sua idade em anos, meses e dias")
    anos = int(input("Anos: "))
    meses = int(input("Meses: "))
    dias = int(input("Dias: "))
    total += dias
    total += DIASMES * meses
    total += DIASANO * anos
    print("Você possui " + str(total) + " dias de vida")


# Exercício 6
def calcula_idade_em_anos_meses_dias():
    dias, meses, anos, idade = 0, 0, 0, 0
    idade = int(input("Informe sua idade em dias:"))
    while idade > 0:
        if idade >= 365:
            anos += 1
            idade -= 365
        elif idade >= 30:
            meses += 1
            idade -= 30
        elif idade >= 1:
            dias += 1
            idade -= 1
    print("Você possui " + str(anos) + " anos, " + str(meses) + " meses e " + str(dias) + " dias de vida")


# Exercício 7
def calcula_media():
    nota1, nota2, nota3, media = 0.0, 0.0, 0.0, 0.0
    print("Informe suas notas:")
    nota1 = float(input("Nota 1:"))
    nota2 = float(input("Nota 2:"))
    nota3 = float(input("Nota 3:"))
    media = ((nota1 * 2) + (nota2 * 3) + (nota3 * 5))/10
    print("Sua média foi: " + str(media))


# Exercício 8
def custo_carro():
    cust_fab, cust_total = 0, 0
    TAXA_DIST = 0.28
    IMPOS = 0.45
    print("Informe o custo de fábrica:")
    cust_fab = int(input())
    cust_total = cust_fab + cust_fab * TAXA_DIST + cust_fab * IMPOS
    print("O custo do carro é de: " + str(cust_total))


# Exercício 9
def escolhe_maior():
    a, b, c, maior = 0.0, 0.0, 0.0, 0.0
    print("Informe três numeros:")
    a = float(input("a:"))
    if a > maior:
        maior = a
    b = float(input("b:"))
    if b > maior:
        maior = b
    c = float(input("c:"))
    if c > maior:
        maior = c
    print("a: " + str(a) + ", b: " + str(b) + " e c: " + str(c))
    print(str(maior) + " é o maior")


# Exercício 10
def calcula_peso_ideal():
    altura, peso = 0.0, 0.0
    sexo = ''
    print("Informe sua altura: ")
    altura = float(input())
    print("Informe seu sexo (M/F): ")
    sexo = input()
    if sexo == 'M':
        peso = (72.7 * altura) - 58
    elif sexo == 'F':
        peso = (62.1 * altura) - 44.7
    print("Seu peso ideal é " + str(peso) + "kg")

# Para executar basta remover o "#" dos comentários abaixo
# calcula_distancia_pontos()
# calcula_idade_dias()
# calcula_idade_anos_meses_dias()
# calcula_idade_em_anos_meses_dias()
# calcula_media()
# custo_carro()
# escolhe_maior()
# calcula_peso_ideal()
