"""
Autores:
Tiago Henrique da Cruz Pereira
João Felipe de Moraes Borges
"""

import threading
import time
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Máximo de conexões/threads simultâneas
MAX_CONEXOES = 11

#Função que raspa os dados dos servidores que recebem mais que o teto estadual
def rasparUSP(pag, nArq):
    #Abertura em modo de escrita do arquivo para super salarios com base no Valor Mensal
    arq = open('USP-ValorMensal'+str(nArq)+'.txt', 'w')

    #For para percorrer todas 895 paginas com os servidores USP
    for j in range(pag,min(896,pag+100)):
        #Criação da "sopa" com os dados da pagina atual do poral de transparencia da USP
        html = urlopen('https://uspdigital.usp.br/portaltransparencia/portaltransparenciaListar?paginar=s&dtainictc=01%2F12%2F2016&nompes=&nomundorg=&nomdepset=&tipcon=&tipcla=&nomabvfnc=&Submit=Solicitar+pesquisa&reload=buscar&imagem=S&print=true&chars=21ni&pag='+str(j))
        bsObj = BeautifulSoup(html, "html.parser")

        #Obtenção dos elementos da tabela com os dados dos servidores
        tabela = bsObj.find("table",{"class":"table_list"})
        #Obtenção dos dados dos elementos da tabela
        tds = tabela.findAll("td")

        #Valor de teto salarial do estado de SP
        teto = 21631.05
        #Vetores para modelar os dados de interesse
        textoVM = []

        #For para percorrer todos os dados excluindo o cabeçalho
        for i in range(14,len(tds),14):
            #Caso o Valor Mensal seja superior ao teto adiciona os dados do servidor ao vetor
            if(float(tds[i+12].getText().strip().replace('.','').replace(',','.'))>=teto):
                textoVM.append('Nome:'+ tds[i].getText() + '\n')
                textoVM.append('Instituto:'+ tds[i+2].getText() + '\n')
                textoVM.append('Função:'+ tds[i+8].getText() + '\n')
                textoVM.append('Salário:'+ tds[i+12].getText() + '\n')
                textoVM.append('\n\n')

                
        #Escreve no respectivo arquivo os dados formatados do servidor com super salario
        arq.writelines(textoVM)
        #Limpa a "sopa"
        bsObj.clear()
        #Exibe qual pagina foi raspada para controle do usuario
        print(j)

    #Fechamento dos arquivos    
    arq.close()

# Thread principal
lista_threads = []
for k in range(MAX_CONEXOES-2):
    while threading.active_count() > MAX_CONEXOES:
        #mostrar_msg("Esperando 1s...")
        time.sleep(1)
    thread = threading.Thread(target=rasparUSP, args=((100*k)+1,k+1,))
    lista_threads.append(thread)
    thread.start()
 
# Esperando pelas threads abertas terminarem
#mostrar_msg("Esperando threads abertas terminarem...")
for thread in lista_threads:
    thread.join()

#Rotina para junção dos arquivos gerados pelas threads em um unico arquivo
for m in range(1,MAX_CONEXOES-1):
    #Seleção de um dos arquivos das threads
    arqui = (open('USP-ValorMensal'+str(m)+'.txt', 'r'))
    path =  os.path.dirname(os.path.realpath(__file__))
    dir = os.listdir(path)
    arquivo = open('USP-ValorMensal.txt', 'a')
    #For para escrever os dados do arquivo selecionado no novo arquivo
    for line in arqui:
        arquivo.writelines(line)
    #For para apagar os arquivos gerados pelas threads
    for arqu in dir:
        if arqu == 'USP-ValorMensal'+str(m)+'.txt':
            arqui.close()
            os.remove(arqu)
arquivo.close()
