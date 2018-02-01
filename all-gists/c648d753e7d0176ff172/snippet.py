#The context of this program is a course of an hour to journalists who know nothing about programming in a lab with Python 3 only. 
import urllib.request
url = 'http://www.portaltransparencia.gov.br/copa2014/api/rest/empreendimento'
resp = urllib.request.urlopen(url).read().decode('utf-8')
total = 0
j = 0
and1 = '<andamento>'
and2 = '</andamento>'
abre = '<valorTotalPrevisto>'
fecha = '</valorTotalPrevisto>'
residuo = 0
while True:
  i1 = resp.find(and1, j)
  if i1 == -1: break
  i2 = resp.find(and2, i1)
  obra_iniciada = not '<id>1</id>' in resp[i1:i2]
  j = resp.find(abre, j)
  k = resp.find(fecha, j)
  print (resp[j+len(abre):k])
  if obra_iniciada: total = total + float (resp[j+len(abre):k])
  j = k + len(fecha)
print ('R$ %.2f' %total)
