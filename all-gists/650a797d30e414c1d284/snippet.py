# -*- coding: UTF-8 -*-#
#
# Isto é um fragmento de código para traduzir certos pydoc's
# que usa o goslate de https://pypi.python.org/pypi/goslate
# LEMBRE: que o Google Tradutor faz traduções literais que
# às vezes pode não fazer sentido. Assim você que dará sentido
# ao texto traduzido conforme o contexto.
#
# Foi criado para o curso Python X-Series (101x). Por isso é 
# interesse que você não copie este código. Assim, abra um 
# editor de texto ou uma IDE e rescreva-o.
# 
# Uso:
# >>> from docgo import help as hp
# >>> hp(dir)
# dir ([objeto]) -> lista de strings
#     Se chamado sem argumentos, retorna os nomes no escopo atual.
#     Caso contrário, retornar uma lista em ordem alfabética de nomes que compreende (alguns de) os atributos
#     do objeto dado, e de atributos alcançáveis a partir dele.
#     ... (conteúdo omitido)
#

import inspect

try:
    import goslate
except ImportError:
    raise TypeError(u"Requer a lib goslate. \n\nUse:\n$ pip install goslate")

def help(obj, lang='pt-br'):
    gs = goslate.Goslate()
    doc = inspect.getdoc(obj)
    doc_translated = gs.translate(doc, lang)
    print doc_translated