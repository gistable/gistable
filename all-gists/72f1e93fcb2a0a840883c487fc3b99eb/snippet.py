import requests
from bs4 import BeautifulSoup

site = requests.get('http://anandabazar.com')
parsed_html = BeautifulSoup(site.text,'lxml')
headlines = parsed_html.find_all('div', {'class': 'leadstoryheading'})
headlines2 = parsed_html.find_all('div',{'class':'leadstorycontent toppadding5'})
for headline in headlines:
    print(str(headline.a.text))

for headline1 in headlines2:
    print(headline1.text)