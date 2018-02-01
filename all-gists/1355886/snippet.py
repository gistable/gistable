def meu_decorator(f):
    def novo_f():
        print 'iniciando f'
        print 'finalizando f'
    return novo_f

@meu_decorator
def minhafuncao():
    print 'dentro da funcao'


minhafuncao()

#o exemplo a seguir funciona da mesma forma que o anterior:
print '-'*30

def meu_decorator(f):
    def novo_f():
        print 'iniciando f'
        print 'finalizando f'
    return novo_f

def minhafuncao():
    print 'dentro da funcao'

minhafuncao = meu_decorator(minhafuncao)


minhafuncao()
