f = open('UFRJ.txt')
dic = {}
for linha in f:
  id_servidor, nome, valor = linha.strip().split(',')
  dic[id_servidor] = [nome, float(valor)]
f.close()

def salário(a): return a[1][1]
maiores = sorted(dic.items(), key=salário, reverse=True)
for f in maiores[:50]:
  print ('%s %.2f %s' %(f[0], f[1][1], f[1][0]))

total = 0
for s in dic:
  total = total + dic[s][1]
print ('Total pago %.2f' %total)

mil = 0
for f in maiores[:1000]:
  mil = mil + f[1][1]
print ('Mil maiores: %.2f' %(mil/total))

menores = sorted(dic.items(), key=salário)
men = 0
cont = 0
for f in menores:
  men = men + f[1][1]
  cont = cont + 1
  if men > mil: break
print ('Mil maiores = %d menores' %cont)

f = open('UFRJ_maiores.txt', 'w')
for s in maiores[:1000]:
  f.write ('%s %.2f %s\n' %(s[0], s[1][1], s[1][0]))

f.close()
