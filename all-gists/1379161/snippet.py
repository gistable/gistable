T = {}
T[1] = (2,3,4)
T[2] = (3,)
T[4] = (2,)


visitei = [0] * 10
ordenacao = []

def visitar(tarefa):
    visitei[tarefa] = 1
    
    if tarefa in T:
        for outra_tarefa in T[tarefa]:
            if visitei[outra_tarefa] == 1:
                raise "ciclo"
                
            if not visitei[outra_tarefa]:
                visitar(outra_tarefa)
            
    visitei[tarefa] = 2
    
    ordenacao.append(tarefa)

visitar(1)
    
print ordenacao
