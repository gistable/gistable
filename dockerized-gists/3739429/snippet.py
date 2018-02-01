#!/usr/bin/python
# -*- coding: utf-8 -*-
## IFRN, Campus Ipanguaçu
## Instrutor: Adorilson Bezerra
## Autor: Jones Romão
## Info4M - Desenvolvimento Web
## 5 de setembro de 2012

import requests as req
import sys

def main(perfis):
    Vperf = open(perfis, "r")
    Vperf = Vperf.readlines()

    DiDados = {}

    print("Procurando...")
    for i in Vperf:
        page = req.get(i.strip("\n"))
        tx = page.text
        VDados = tx.split("\n")
        for j in range(len(VDados)):
            if("about_container" in VDados[j]):
                Nome = VDados[j + 2]
            elif("Points earned all time" in VDados[j]):
                PontosT = VDados[j + 2]
                DiDados[Nome] = PontosT
                break

    print("Nome", "Pontos")
    for i in DiDados:
        print(i.strip(" "), DiDados[i].strip(" "))

if __name__ == "__main__":
    perfis = sys.argv[1]
    main(perfis)