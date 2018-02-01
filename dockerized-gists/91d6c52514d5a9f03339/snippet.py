#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import re
import sys
import base64
import subprocess
import urllib
import lxml.etree
import StringIO


# Depuração ativa ou não
DEBUG = False


# Imprimi dados para depuração
def debug(status, resposta, headers, html):
    global DEBUG
    if DEBUG or status >= 400:
        print '=' * 100
        print 'Resposta:', status, resposta.reason
        print 'Headers:'
        for h in headers:
            print h
        print '-' * 100
        print repr(html)
        print '=' * 100
        if status >= 400:
            print 'Erro ao acessar o site!'
            sys.exit(0)

# Visualizador de imagens, eog no Linux/Gnome
VIZUALIZADOR_DE_IMAGEM = 'eog'

# Visualizador de páginas HTML, iceweasel no Linux/Gnome
VIZUALIZADOR_HTML = 'iceweasel'

# Entradas ocultas e fixas
inputs = [
    ('__EVENTTARGET', ''),
    ('__EVENTARGUMENT', ''),
    ('__VIEWSTATEGENERATOR', 'B5B0D4D0'),
    ('ctl00$txtPalavraChave', ''),
    ('hiddenInputToUpdateATBuffer_CommonToolkitScripts', '1'),
    ('ctl00$ContentPlaceHolder1$btnConsultar', 'Continuar')]

# Pede pela chave de acesso e adiciona às entradas
chave = raw_input('Chave de acesso: ')
inputs.append(('ctl00$ContentPlaceHolder1$txtChaveAcessoCompleta', chave))

# Conexão com o site da fazenda
conexao = httplib.HTTPConnection('www.nfe.fazenda.gov.br')

# Requerer a página inicial
conexao.request('GET', '/portal/consulta.aspx?'
                'tipoConsulta=completa&tipoConteudo=XbSeqxE8pl8%3d')
resposta = conexao.getresponse()
status = resposta.status
headers = resposta.getheaders()
html = resposta.read()
debug(status, resposta, headers, html)

# Extrai a imagem do captcha do html em base64
img_src = re.sub('^.*<img id="ContentPlaceHolder1_imgCaptcha"'
                 ' src="data:image/png;base64,([^"]*)".*$',
                 r'\1', html.replace('\n', '').replace('\r', ''))

# Salva a imagem do captcha e mostra a mesma
with open('captcha.png', 'w') as arquivo:
    arquivo.write(base64.b64decode(img_src))
subprocess.call([VIZUALIZADOR_DE_IMAGEM, 'captcha.png'])

# Pergunta o captcha
captcha = raw_input('Captcha: ')

# Adiciona o captcha nas entradas
inputs.append(('ctl00$ContentPlaceHolder1$txtCaptcha', captcha))

# Adiciona outras entradas ocultas no html
hidden_inputs = re.findall('<input [^>]*type="hidden"[^>]*>', html)
inputs.extend([(re.sub('^.*name="([^"]+).*$', r'\1', i),
                re.sub('^.*value="([^"]+).*$', r'\1', i))
               for i in hidden_inputs])

# Prepara POST
dados = urllib.urlencode(dict(inputs))
cookie = dict(headers)['set-cookie'].split(';')[0]
cabecalhos = {'Content-Type': 'application/x-www-form-urlencoded',
              'Cookie': cookie}

# Faz o POST
conexao.request('POST', '/portal/consulta.aspx?'
                'tipoConsulta=completa&tipoConteudo=XbSeqxE8pl8%3d',
                dados, cabecalhos)
resposta = conexao.getresponse()
status = resposta.status
headers = resposta.getheaders()
html = resposta.read()
debug(status, resposta, headers, html)

# Requer a página completa dos dados da NFe
conexao.request('GET', '/portal/consultaImpressao.aspx?tipoConsulta=completa',
                None, cabecalhos)
resposta = conexao.getresponse()
status = resposta.status
headers = resposta.getheaders()
html = resposta.read()
debug(status, resposta, headers, html)

# Salva o HTML com os dados da NFe e mosta no navegador
with open('nfe.html', 'w') as arquivo:
    arquivo.write(html)
subprocess.call([VIZUALIZADOR_HTML, 'nfe.html'])

# Decodifica o html
charset = re.sub('^.*charset=([^ ;]*).*$', r'\1',
                 dict(headers)['content-type'])
html = html.decode(charset)

# Usando lxml para navegar nas tags HTML
parser = lxml.etree.HTMLParser()
doc = lxml.etree.parse(StringIO.StringIO(html), parser)
root = doc.getroot()
# ...
# Aqui trabalha-se cada tag do HTML para formar o XML
# ...

# ---------- Somente para melhor visualizar os resultados ----------

# Limpando as tags HTML para ver melhor dos dados de forma textual

# Retirando espaços extras
dados = re.sub('>\s+', '>', re.sub('\s+<', '<', html))
# Colocando ':' entre rótulo e valor
dados = dados.replace('</label>', ': ')
# Quebrando linhas
dados = dados.replace('</td>', '\n').replace('</legend>', '\n')
# Retirando as tags HTML
dados = re.sub('<[^>]+>', '', dados)

print dados
