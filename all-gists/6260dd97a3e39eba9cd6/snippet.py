#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PyGTK 3 é incompatível com Pole
try:
    # Caso tiver PyGTK 2
    import pygtk
    pygtk.require("2.0")
    import gtk
    PixbufLoader = gtk.gdk.PixbufLoader
    timeout_add = gtk.timeout_add
    shadow_in = gtk.SHADOW_IN
    policy_automatic = gtk.POLICY_AUTOMATIC
    fill = gtk.FILL
    tem_gtk = True
    print 'Usando PyGTK 2'
except:
    # Caso que não tem GTK
    tem_gtk = False

import re
import httplib
import urllib2
import base64
import cStringIO
import time
import pole

cookie = ''
entradas = {}

def erro(resposta, conexao):
    if tem_gtk:
        erro = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xb4\x00\x00\x002\x01\x03\x00\x00\x00\xcf\xeac\xb4\x00\x00\x00\x06PLTE\xff\xff\xff\x00\x00\x00U\xc2\xd3~\x00\x00\x00CIDAT8\xcbc`\x18\x05\xc3\n0\xff\x01\x12l$\x883\xe0\x12\xcf\xcb\x93\xc3*^WW\xdf\x86\xcd\xfc\x82\x82D\xac\xe2\t\t\x07\x8ea3\x87\x0c\xf1\x03\xd8\xc5\x13\x1b\xb0\xdb[\x8f\xc3=\xd8\xfc5\n\x86\x04\x00\x00\x83H\x18F\x0e\x02\xd2\xa7\x00\x00\x00\x00IEND\xaeB`\x82'
        l = gtk.gdk.PixbufLoader()
        l.write(erro)
        l.close()
        i.set_from_pixbuf(l.get_pixbuf())
        e1.set_text(resposta.reason)
        e2.set_text(str(resposta.status))
    print 'Erro: %i - %s' % (reposta.status, reposta.reason)
    conexao.close()

def ler_captch_png(diretorio = None):
    global cookie
    conexao = httplib.HTTPConnection('www.nfe.fazenda.gov.br')
    conexao.request('GET', '/portal/consulta.aspx?tipoConsulta=completa&tipoConteudo=XbSeqxE8pl8%3d')
    resposta = conexao.getresponse()
    if resposta.status != 200:
        erro()
        return

    cookie = 'duracao_visita=9ce8b9e7-6546-30c2-f4e5-b3ba72385c1f; nova_visita_dia=1b1c2c52-3ee2-26a9-44bd-25750c5b36df; nova_visita_mes=1b1c2c52-3ee2-26a9-44bd-25750c5b36df; nova_visita_ano=1b1c2c52-3ee2-26a9-44bd-25750c5b36df; ' + resposta.getheader('set-cookie').split(';', 1)[0]
    atualizar_captcha(resposta, conexao, diretorio)

def atualizar_captcha(resposta, conexao, diretorio):
    html = resposta.read().replace('\r\n', '')
    conexao.close()

    for entrada in re.findall(r'<input (?![^>]*type="image")(?![^>]*btnLimpar)[^>]*>', html):
        name = re.sub(r'^.*name="([^"]+)".*$', r'\1', entrada)
        value = re.sub(r'^.*value="([^"]+)".*$', r'\1', entrada) if ' value="' in entrada else ''
        entradas[name] = value

    img = re.sub('^.*<img id="ContentPlaceHolder1_imgCaptcha" src="data:image/png;base64,([^"]+)".*$',
                 r'\1', html, re.DOTALL)
    captcha_png = base64.b64decode(img)
    if tem_gtk:
        l = PixbufLoader()
        l.write(captcha_png)
        i.set_from_pixbuf(l.get_pixbuf())
        l.close()
        del l

    if diretorio:
        with open(diretorio + '/captcha.png', 'wb') as c:
            c.write(captcha_png)

def ler_dados(chave = None, captcha = None, diretorio = None):
    dados = []
    if tem_gtk:
        chave = e1.get_text()
        captcha = e2.get_text()
    for name, value in entradas.items():
        if 'txtCaptcha' in name:
            value = captcha
        elif 'txtChaveAcessoCompleta' in name:
            value = chave
        dados.append(urllib2.quote(name, '') + '=' + urllib2.quote(value, ''))
    dados = '&'.join(dados)
    conexao = httplib.HTTPConnection('www.nfe.fazenda.gov.br')
    conexao.request('POST', '/portal/consulta.aspx?tipoConsulta=completa&tipoConteudo=XbSeqxE8pl8%3d',
                    dados, {'Cookie': cookie, 'Content-Length': len(dados),
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
    resposta = conexao.getresponse()
    if resposta.status == 200:
        atualizar_captcha(resposta, conexao, diretorio)
        return
    if resposta.status != 302:
        erro(resposta, conexao)
        return
    location = resposta.getheader('location')
    conexao.close()
    conexao = httplib.HTTPConnection('www.nfe.fazenda.gov.br')
    conexao.request('GET', location, headers = {'Cookie': cookie})
    while True:
        try:
            resposta = conexao.getresponse()
            break
        except Exception as err:
            print repr(err)
            time.sleep(1)
    if resposta.status != 200:
        erro(resposta, conexao)
        return

    html = resposta.read().lstrip()
    conexao.close()

    html = pole.xml.importar(html, True)
    campos = {}
    for registro in pole.xml.procurar(html, 'fieldset'):
        campos[str(registro.legend)] = dict(zip(
            [str(l) for l in pole.xml.procurar(registro, 'label')],
            [str(v) for v in pole.xml.procurar(registro, 'span')]))

    txt = str(campos).replace('{', '{\n').replace('\', ', '\',\n').replace('},', '},\n\n')

    if tem_gtk:
        tb.set_text(txt)

    if diretorio:
        with open('%s/%s.txt' % (diretorio, chave), 'wb') as f:
            f.write(txt)

if tem_gtk:
    # Widgets
    w = gtk.Window()
    t = gtk.Table()
    i = gtk.Image()
    l1 = gtk.Label('Chave:')
    e1 = gtk.Entry()
    l2 = gtk.Label('Captcha:')
    e2 = gtk.Entry()
    b = gtk.Button('Baixar NF-e')
    s = gtk.ScrolledWindow()
    tb = gtk.TextBuffer()
    tv = gtk.TextView()
    # Configurações
    w.set_title('Capturar dados da NF-e')
    w.set_border_width(5)
    w.connect('delete-event', gtk.main_quit)
    t.set_row_spacings(5)
    t.set_col_spacings(5)
    aguarde = "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xb4\x00\x00\x002\x01\x03\x00\x00\x00\xcf\xeac\xb4\x00\x00\x00\x06PLTE\xff\xff\xff\x00\x00\x00U\xc2\xd3~\x00\x00\x00\x95IDAT8\xcbc`\x18\x05C\x17\x1c@\x17H Q\xfc\x03.q\xb9c\x12\x15\xe6r\x07?\xa0\n3\xce\xb0?&\xf1\xc7\xde\xfe\xf8\x0ft\xf1\xc2c\x12}\x16\x85\xc7d\xd0\xc5\x13\x8eI\xb0\x19$\x9c\xe1A\x15g\xe6\x01\x8a\xd7\x19$\x9c\xff\x83&\xfe'\xe1\x98\xe4?Lq\xf6\x7f@\xf16\xa09h\xcedc+<n\xd9gPx\x8c\x05]\xdc\xfe\xf0\xcf\x7f\x06\xf6\xc7\xff\x1cF\xb1\x99\x87Y\xee\xf0\x8do\x06r\x07\x7f\x1c\xe6!\x14\x94\x10\xa0\xd8\x80]\xdc\x1e\x87\xb8\xfch\xa2\xa4)\x00\x00\x0c`4\x82s~Nb\x00\x00\x00\x00IEND\xaeB`\x82"
    l = PixbufLoader()
    l.write(aguarde)
    l.close()
    i.set_from_pixbuf(l.get_pixbuf())
    e1.set_width_chars(44)
    b.connect('clicked', ler_dados)
    s.set_shadow_type(shadow_in)
    s.set_policy(policy_automatic, policy_automatic)
    tv.set_buffer(tb)
    # Estrutura
    w.add(t)
    t.attach(i, 0, 1, 0, 2, yoptions = fill)
    t.attach(l1, 1, 2, 0, 1, yoptions = fill)
    t.attach(e1, 2, 4, 0, 1, yoptions = fill)
    t.attach(l2, 1, 2, 1, 2, yoptions = fill)
    t.attach(e2, 2, 3, 1, 2, yoptions = fill)
    t.attach(b, 3, 4, 1, 2, yoptions = fill)
    t.attach(s, 0, 4, 2, 3)
    s.add(tv)
    w.show_all()
    timeout_add(1000, ler_captch_png)
    gtk.main()
else:
    print 'Capturar dados da NF-e'
    diretorio = raw_input('Diretório para o captcha.png e <nfe>.txt: ')
    print 'Aguarde...'
    ler_captch_png(diretorio)
    if not cookie:
        print 'Tente novamente...'
    else:
        print 'Abra o arquivo %s/captcha.png e veja a imagem...' % diretorio
        captcha = raw_input('Captcha: ')
        chave = raw_input('Chave: ')
        ler_dados(chave, captcha, diretorio)
        print 'Dados salvos em %s/%s.txt' % (diretorio, chave)
