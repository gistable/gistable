#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests,json,sys

# Script simples para consulta de dados na base dados nacional do SUS utilizando o CPF.
# Jhonathan Davi A.K.A jh00nbr / Insightl4b lab.insightsecurity.com.br
# jh00nbr: http://jhonathandavi.com.br
# Blog: lab.insightsecurity.com.br
# Github: github.com/jh00nbr
# Twitter @jh00nbr

try:
    config = {'api_sus':'http://dabsistemas.saude.gov.br/sistemas/sadab/js/buscar_cpf_dbpessoa.json.php?cpf=', 'cpf':sys.argv[1]}
    req = requests.get(config['api_sus']+config['cpf'])
    dados = json.loads(req.content.decode("utf-8"))
    # Retorna os dados no formato <nome_pessoa> / <numero_cpf> / <data_nascimento> / <nome_mae>"
    print ("Nome: ", dados['NO_PESSOA_FISICA'], "\nCPF: ", dados['NU_CPF'], "\nData de nascimento:", dados['DT_NASCIMENTO'], "\nNome da mãe: ", dados['NO_MAE'])
    # NU_CPF, NO_PESSOA_FISICA, DT_NASCIMENTO, CO_SEXO, NO_MAE, DS_SEXO
except IndexError:
    print ("Entrada inválida! Adicione o CPF válido como argumento.\nEx.: ~$ python cpf_consulta_api_sus.py 00000000000")