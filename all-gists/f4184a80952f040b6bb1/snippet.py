import urllib.request
import json
url = 'http://educacao.dadosabertosbr.com/api/escolas?nome='
escola = 'embraer'
resp = urllib.request.urlopen(url+escola).read()
resp = json.loads(resp.decode('utf-8'))
for x in resp[1]:
  print (x['nome'])
  print ('Código:', x['cod'])
  print (x['cidade'], x['estado'])
  print (x['enemMediaGeral'], x['situacaoFuncionamentoTxt'])
  print ()