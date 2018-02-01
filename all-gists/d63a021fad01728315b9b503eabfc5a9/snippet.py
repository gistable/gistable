import requests
from bs4 import BeautifulSoup

sitemap = 'http://www.nasa.gov/sitemap/sitemap_nasa.html'

r = requests.get(sitemap)
html = r.content

soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all('a')
urls = [link.get('href') for link in links
        if link.get('href') and link.get('href')[0:4]=='http']

results = []
for i, url in enumerate(urls,1):
    try:
        r = requests.get(url)
        report = str(r.status_code)
        if r.history:
            history_status_codes = [str(h.status_code) for h in r.history]
            report += ' [HISTORY: ' + ', '.join(history_status_codes) + ']'
            result = (r.status_code, r.history, url, 'No error. Redirect to ' + r.url)
        elif r.status_code == 200:
            result = (r.status_code, r.history, url, 'No error. No redirect.')
        else:
            result = (r.status_code, r.history, url, 'Error?')
    except Exception as e:
        result = (0, [], url, e)
        
    results.append(result)

#Sort by status and then by history length
results.sort(key=lambda result:(result[0],len(result[1])))

#301s - may want to clean up 301s if you have multiple redirects
print('301s')
i = 0
for result in results:
    if len(result[1]):
        i += 1
        print(i, end='. ')
        for response in result[1]:
            print('>>', response.url, end='\n\t')
        print('>>>>',result[3])
        
#non-200s
print('\n==========\nERRORS')
for result in results:
    if result[0] != 200:
        print(result[0], '-', result[2])