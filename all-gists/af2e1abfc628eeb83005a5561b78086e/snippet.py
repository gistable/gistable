def soma(dados):
  if dados == [ ]:
    return 0

  else:
    if ehAtomo(car(dados)):
      return car(dados) + soma(cdr(dados))
    else:
      return soma(car(dados)) + soma(cdr(dados))
      
#### ======================== SUBPROGRAMAÇÃO =====================### 
def car(lis):
  return lis[0]
  
def cdr(lis):
  return lis[1:]
  
def cons(x, lis):
  return [x]+lis
  
def ehLista(x):
  return isinstance(x, list)

def ehAtomo(x):
  return not ehLista(x)
  
def maior (lista):
	if lista == [ ]:
		return 0
	else: 
		return max(lista)
		
def mediaPositivos(lista):
	
	if lista == [ ]:
		return 0
	else: 
		if car(lista) < 0:
			del lista[0]
			mediaPositivos(lista)
		
		return sum(lista)/len(lista)

## ===================================PROGRAMA ====================# 

entrada = [1,-3,3,4,5,6,7]

print(mediaPositivos(entrada))
