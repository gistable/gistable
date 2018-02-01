import urllib.request
url = 'http://www.portaltransparencia.gov.br/copa2014/api/rest/empreendimento'
resp = urllib.request.urlopen(url).read().decode('utf-8')
total = 0
j = 0
while True:
  abre = '<valorTotalPrevisto>'
  fecha = '</valorTotalPrevisto>'
  j = resp.find(abre, j)
  if j == -1:
    break
  k = resp.find(fecha, j)
  print (resp[j+len(abre):k])
  total = total + float (resp[j+len(abre):k])
  j = k + len(fecha)
print ('R$ %.2f' %total)