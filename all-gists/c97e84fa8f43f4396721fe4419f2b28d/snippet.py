# Primo:
# Exceto 2, não pode ser par.
# Deve ser divisivel somente por 1 e por ele mesmo.
# Não pode ter outro divisor.
def ehPrimo(n):
    divisivel = 0
    x = 2
    while x <= n:
        #print("Dividindo", n, "por", x)
        if (n % x == 0):
            #print("eh divisivel por", x)
            divisivel = divisivel + 1
        x = x+1
    if divisivel > 1:
        #print("Nao eh primo.")
        return 0
    else:
        print(n, "Eh primo.")
        return 1

num = int(input("Digite um valor inteiro: "))
cont = 0
if ehPrimo(num):
    print("Entao vamos começar a procurar os 10 próximos primos!")
    while cont < 10:
        num = num + 1
        if ehPrimo(num):
            cont = cont + 1
else:
    print("Sem primos.")
