# coding=utf-8
"""
NAO FUNCIONA MAIS. O sistema de CAPTCHA foi trocado.
**Implementa um Webcrawler para extracao de dados da pesquisa de media de precos realizada periodicamente pela ANP**
Desenvolvido por Fabio C. Barrionuevo da Luz. - 2013
Simple crawler to ANP site
Copyright (C) 2013  Fabio C. Barrionuevo da Luz.
 
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 
dependencias:

do sistema:
sudo apt-get install libxml2-dev libxslt-dev python-dev

python2:

wget -H https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py; sudo -H python2 /tmp/get-pip.py virtualenv virtualenvwrapper -U;
sudo -H pip2 install splinter lxml


"""
 
import re
try:
    from splinter import Browser
except ImportError:
    print('please, install splinter\npip install splinter')
try:
    from lxml import html
except ImportError:
    print('please, install lxml\npip install lxml')
 
from time import sleep
 
 
XPATH_MEDIA = '//*[@id="postos_nota_fiscal"]/fieldset/div[1]/table/tbody/tr[2]/td[2]/text()'
XPATH_DESVIO_PADRAO = '//*[@id="postos_nota_fiscal"]/fieldset/div[1]/table/tbody/tr[3]/td[2]/text()'
XPATH_VALOR_MINIMO = '//*[@id="postos_nota_fiscal"]/fieldset/div[1]/table/tbody/tr[4]/td[2]/text()'
XPATH_VALOR_MAXIMO = '//*[@id="postos_nota_fiscal"]/fieldset/div[1]/table/tbody/tr[5]/td[2]/text()'
XPATH_PERIODO_APURACAO = '//*[@id="conteudo"]/div/div/h3[3]/text()'
 
# mas que captcha ingenuo
XPATH_CAPTCHA_LETRA1 = '//*[@id="letra1"]'
XPATH_CAPTCHA_LETRA2 = '//*[@id="letra2"]'
XPATH_CAPTCHA_LETRA3 = '//*[@id="letra3"]'
XPATH_CAPTCHA_LETRA4 = '//*[@id="letra4"]'
 
# XPATH_INPUT_CAPTCHA = '//*[@id="txtValor"]'
 
 
 
 
XPATH_TABELA = '//*[@id="postos_nota_fiscal"]/div/table'
 
COMBUSTIVEIS = (('Gasolina', '487*Gasolina'),
                ('Diesel', '532*Diesel'),
                ('Diesel S10', '812*Diesel@S10'),
                ('Etanol', '643*Etanol'))
 
COMPILED_RE_CARACTERES_REMOVER = re.compile('[A-Za-z \\\:\[\]]')
 
 
def _verificar_preco(browser, nome_combustivel, cod_combustivel):
    """
    Executa o crawler e
    Retorna um dicionario com os dados resultantes da pesquisa de media de preço
    de combustivel, realizadas periodicamente ANP.
 
    :browser: Instancia do Splinter Browser ( splinter.cobrateam.info )
 
    :nome_combustivel: Nome do combustivel
 
    :cod_combustivel: Codigo do Combustivel no padrao do site da ANP
 
    """
    
    print('Verificando combustivel {0}'.format(nome_combustivel))
    url = "http://www.anp.gov.br/preco/"
    #navega para a pagina principal
    browser.visit(url)
 
    button = browser.find_link_by_text('Por Estado')
    #navega para a segunda pagina
    button.click()
    sleep(1)
 
 
    browser.select('selEstado', 'TO*TOCANTINS')
    browser.select('selCombustivel', cod_combustivel)
    tree = html.fromstring(browser.html)
    
    letra1 = '{0}'.format((tree.xpath(XPATH_CAPTCHA_LETRA1))[0].text)
    letra2 = '{0}'.format((tree.xpath(XPATH_CAPTCHA_LETRA2))[0].text)
    letra3 = '{0}'.format((tree.xpath(XPATH_CAPTCHA_LETRA3))[0].text)
    letra4 = '{0}'.format((tree.xpath(XPATH_CAPTCHA_LETRA4))[0].text)
    caixa_texto = browser.find_by_id('txtValor')
    caixa_texto.fill("{0}{1}{2}{3}".format(letra1, letra2, letra3, letra4))
    button = browser.find_by_id('image1')
 
    #navega para a terceira pagina
    button.click()
    sleep(1)
 
    button = browser.find_link_by_text('Palmas')
    #navega para a quarta pagina
    button.click()
    sleep(1)

    tree = None
    tree = html.fromstring(browser.html)

    # http://stackoverflow.com/questions/20418807/python-parse-html-table-using-lxml
    XPATH_TABELA = '//tr/td//text()'

    #b = tree.xpath(XPATH_TABELA)
    for tbl in tree.xpath('//table'):
    	elements = tbl.xpath('.//tr/td//text()')
    	print(elements)
    #print(b)
 	
 	

    a = '{0}'.format(tree.xpath(XPATH_PERIODO_APURACAO))
    a = a.replace('a', '-')
 
    PERIODO_APURACAO = re.sub(COMPILED_RE_CARACTERES_REMOVER, "", a)
    V_MEDIA = '{0}'.format((tree.xpath(XPATH_MEDIA))[0])
    V_DESVIO_PADRAO = '{0}'.format((tree.xpath(XPATH_DESVIO_PADRAO))[0])
    V_VALOR_MINIMO = '{0}'.format((tree.xpath(XPATH_VALOR_MINIMO))[0])
    V_VALOR_MAXIMO = '{0}'.format((tree.xpath(XPATH_VALOR_MAXIMO))[0])
 
    cotacao = {nome_combustivel: {
        'periodo_apuracao': PERIODO_APURACAO,
        'media': V_MEDIA,
        'desvio_padrao': V_DESVIO_PADRAO,
        'valor_minimo': V_VALOR_MINIMO,
        'valor_maximo': V_VALOR_MAXIMO}}
 
    return cotacao
 
 
def verificar_precos_combustiveis():
    """
    Executa o crawler e
    Retorna um dicionario com os dados resultantes da pesquisa de media de preço
    realizadas periodicamente ANP, para todos os combustiveis disponiveis,
 
    """
 
    cotacao = []
 
#    with Browser('phantomjs') as browser:
    #with Browser('zope.testbrowser') as browser:
    with Browser() as browser:
        for nome_combustivel, cod_combustivel in COMBUSTIVEIS:
            cotacao.append(_verificar_preco(browser, nome_combustivel, cod_combustivel))
 
    return cotacao
 
 
if __name__ == "__main__":
    import pprint
    result = verificar_precos_combustiveis()
    pprint.pprint(result, width=20)