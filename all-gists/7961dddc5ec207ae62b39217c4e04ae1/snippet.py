# -*- coding: utf-8 -*-

'''
	O SUAP (Sistema Unificado de Administração Pública) utiliza
	o seguinte diretório para guardar as fotos de alunos
	cadastrados: /media/alunos/. Todas as fotos contém apenas
	números e extensão .jpg, desse modo, podemos utilizar o
	seguinte código para obter todas as imagens em um determinado
	período.
'''

import urllib

inicio = int(input('Início: '))
fim = int(input('Fim: '))

for i in range(inicio, fim):
	string = 'https://suap.ifrn.edu.br/media/alunos/' + str(i) + '.jpg'
	print ('Baixando: %s' %string)
	urllib.urlretrieve(string, str(i) + '.jpg')