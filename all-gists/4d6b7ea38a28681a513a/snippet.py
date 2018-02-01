#The context of this program is a course of an hour to journalists who know nothing about programming in a lab with Python 3 only.
import urllib.request
import json

def analisa_detalhe(cod):
  url = 'http://educacao.dadosabertosbr.com/api/escola/'
  resp = urllib.request.urlopen(url+str(cod)).read()
  resp = json.loads(resp.decode('utf-8'))
  if int(resp['salasExistentes']) > 1:
    print ('Salas Existentes:', resp['salasExistentes'])
    print ('Funcionários:', resp['funcionarios'])
    print ('Queima Lixo:', resp['lixoQueima'])
    print ('Sanitário Fora Predio:', resp['sanitarioForaPredio'])
          
url = 'http://educacao.dadosabertosbr.com/api/escolas/buscaavancada?situacaoFuncionamento=1&energiaInexistente=on&aguaInexistente=on&esgotoInexistente=on'
resp = urllib.request.urlopen(url).read()
resp = json.loads(resp.decode('utf-8'))
print ('Número de Escolas em funcionamento sem energia, água e esgoto:', resp[0])
for x in resp[1]:
  print (x['nome'], x['cod'])
  print (x['cidade'], x['estado'], x['regiao'])
  analisa_detalhe(x['cod'])
  print ()