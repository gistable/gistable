import urllib.request
import json
url = 'http://educacao.dadosabertosbr.com/api/escolas/buscaavancada?situacaoFuncionamento=1&energiaInexistente=on&aguaInexistente=on&esgotoInexistente=on'
resp = urllib.request.urlopen(url).read()
resp = json.loads(resp.decode('utf-8'))
print ('Número de Escolas em funcionamento sem energia, água e esgoto:', resp[0])
for x in resp[1]:
  print (x['nome'], x['cod'])
  print (x['cidade'], x['estado'], x['regiao'])
  print ()
  
