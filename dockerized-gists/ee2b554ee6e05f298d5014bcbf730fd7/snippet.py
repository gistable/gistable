import requests
from bs4 import BeautifulSoup as bs
import string

pets = []
for pet in ('Gatos', 'Caes'):
  for letra in string.ascii_uppercase:
    for k in (1, 2, 3):
      u = 'https://www.bayerpet.com.br/%s/lista-nomes/%s%s' %(pet, letra, str(k))
      p = requests.get(u)
      s = bs(p.content, 'html.parser')
      lista = s.find('ul', class_='list listNames')
      nomes = lista.findAll('li')
      pets.extend([n.string.lower() for n in nomes])

pets = list(set(pets))
pets.sort()
print (' '.join(pets))