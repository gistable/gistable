#A ideia inicial partiu deste código https://gist.github.com/duarteguilherme/25a80afd502035c55b45ed85dc8977e0
import requests
import json
import csv
headers = {
'Host': 'www.cnj.jus.br',
'Connection': 'keep-alive',
'Content-Length': '213',
'Accept': 'application/json, text/plain, */*',
'Origin': 'http://www.cnj.jus.br',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
#Observe que o User-Agent pode ser diferente na sua configuração. Inspecione e veja em Network All seu User-Agent
'Content-Type': 'application/json;charset=UTF-8',
'Referer': 'http://www.cnj.jus.br/bnmp/',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}
cnjp = 'http://www.cnj.jus.br/bnmp/rest/pesquisar'
cnjd = 'http://www.cnj.jus.br/bnmp/rest/detalhar'
#AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO
uf = 'AC'
pag_ini = 1 #valor inicial 1, se o servidor te derrubar, retome mudando este número
if pag_ini == 1:
    f = open(f'cnj_presos_{uf}.csv', 'a')
    w = csv.writer(f)
    rotulos = '''id num_mandado situacao data validade assuntos municipio
                 nomes sexos pais maes nacionalidades naturalidades
                 dt_nascimentos profissoes enderecos motivo recaptura
                 sintese pena regime'''.split()
    w.writerow(rotulos)
    f.close()
payload_ini = '''{"criterio":{"orgaoJulgador":{"uf":"%s","municipio":"",
              "descricao":""},"orgaoJTR":{},"parte":{"documentos":
              [{"identificacao":null}]}},"paginador":{},
              "fonetica":"true","ordenacao":{"porNome":false,
              "porData":false}}''' %uf

def faz_req(url, payload, headers):
    requests.adapters.DEFAULT_RETRIES = 100
    p = requests.post(url, data = payload, headers = headers)
    return p.text

resp = faz_req(cnjp, payload_ini, headers)
n_pag = json.loads(resp)['paginador']['totalRegistros'] // 10
print (f'Total páginas: {n_pag}')
for k in range(pag_ini, n_pag + 1):
    print (f'{uf} Página: {k}')
    f = open(f'cnj_presos_{uf}.csv', 'a')
    w = csv.writer(f)
    payload_pag = '''{"criterio":{"orgaoJulgador":{"uf":"%s",
     "municipio":"","descricao":""},"orgaoJTR":{},
     "parte":{"documentos":[{"identificacao":null}]}},
     "paginador":{"paginaAtual":%d},"fonetica":"true",
     "ordenacao":{"porNome":false,"porData":false}}''' %(uf, k)
    resp = faz_req(cnjp, payload_pag, headers)
    mandados = json.loads(resp)['mandados']
    headers['Content-Length'] = '13'
    for m in mandados:
        payload_detalhe = '{"id": %d}' %m['id']
        resp = faz_req (cnjd, payload_detalhe, headers)
        detalhes = json.loads(resp)
        if detalhes['sucesso'] == False: #não tenho permissão para esse
            print ('Sem permissão %s' %m['numeroMandado'])
            continue
        detalhes = detalhes['mandado']
        for x in detalhes:
          if detalhes[x] == None: detalhes[x] = ''
          if type(detalhes[x]) is list and detalhes[x][0] == None: detalhes[x] = ''
          
        id_ = str(m['id'])
        num_mandado = detalhes['numero']
        situacao = detalhes['situacao']
        data = detalhes['data']
        validade = detalhes['validade']
        assuntos = '/'.join(detalhes['assuntos'])
        municipio = detalhes['municipio']
        nomes = '/'.join(detalhes['nomes'])
        sexos = ' '.join(detalhes['sexos'])
        pais = ' '.join(detalhes['genitores'])
        maes = ' '.join(detalhes['genitoras'])
        nacionalidades = ' '.join(detalhes['nacionalidades'])
        naturalidades = ' '.join(detalhes['naturalidades'])
        dt_nascimentos = ' '.join(detalhes['datasNascimentos'])
        profissoes = ' '.join(detalhes['profissoes'])
        enderecos = '/'.join(detalhes['enderecos'])
        motivo = detalhes['motivo']
        recaptura = detalhes['recaptura']
        sintese = detalhes['sintese']
        pena = detalhes['pena']
        regime = detalhes['regime']
        
        row = [id_, num_mandado, situacao, data, validade, assuntos,
        municipio, nomes, sexos, pais, maes, nacionalidades,
        naturalidades, dt_nascimentos, profissoes, enderecos,
        motivo, recaptura, sintese, pena, regime]
        w.writerow(row)
    f.close()
    headers['Content-Length'] = '213'
