#Laura Maia e Letícia Barreto
import requests
from bs4 import BeautifulSoup
url='https://pt.wikipedia.org/wiki/Os_100_livros_do_s%C3%A9culo_segundo_Le_Monde'
soup = BeautifulSoup(requests.get(url).text, 'html.parser')

nome=[nome.string.strip()
      for nome in soup.findAll('i')]

ranking=[rank.string
         for rank in soup.findAll('td', {'align':"right"})]

livros = [{'Ranking': x, 'Nome': y}
          for x , y in zip(ranking, nome)]

for livro in livros:
    print ('{} {}'.format(livro['Ranking'], livro['Nome']))


