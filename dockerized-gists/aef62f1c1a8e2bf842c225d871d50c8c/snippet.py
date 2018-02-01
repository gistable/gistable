# -*- coding: utf-8 -*-

import base64, urllib
import requests
import os, re, sys

from bs4 import BeautifulSoup

def _crack(code):

        zeros = ''
        ones = ''
        for n,letter in enumerate(code):
            if n % 2 == 0:
                zeros += code[n]
            else:
                ones = code[n] + ones

        key = zeros + ones
        key = list(key)
        i = 0

        while i < len(key):
            if key[i].isdigit():
                for j in range(i+1,len(key)):
                    if key[j].isdigit():
                        u = int(key[i])^int(key[j])
                        if u < 10: 
                            key[i] = str(u)
                        i = j					
                        break
            i+=1

        key = ''.join(key).decode('base64')[16:-16]

        return key

def _decrypt(url):
    adfly = urllib.urlopen(url).read()
    ysmm = re.findall(r"var ysmm = '(.*?)';",adfly)[0]
    decrypted_url = _crack(ysmm)

    return decrypted_url

def main():
    target  = "https://www.fiuxy.bz/threads/fairy-tail-manga-tomos-52-especiales-spin-off-espanol-mg-actualizable.4115815/"

    content = requests.get(target).text
    soup    = BeautifulSoup(content, 'html.parser')
    items   = soup.select('article blockquote div')
    links   = []

    for item in items:
        for a in item.find_all('a'):
            if a.text == "www.Mega.com":
                url = re.search('http://adf(.*)', a.get('href'))
                links.append("http://adf{}\n".format(url.group(1)))

    if not os.path.exists('output'):
        os.mkdir('output')

    file = open('output/output.txt', 'w')

    try:
        for index, link in enumerate(links):
            print "Procesando enlace #{} de {}".format(index + 1, len(links))
            file.write("{}\n".format(_decrypt(link)))

    except Exception as e:
        print "Ocurrió un error: {}".format(e)

    print "¡Finalizado! Resultados guardados en output/output.txt"

if __name__ == "__main__":
    main()