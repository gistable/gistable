def get_n_results_dumb(q):
    r = requests.get('http://www.google.com/search',
                     params={'q': q,
                             "tbs": "li:1"})
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text)
    s = soup.find('div', {'id': 'resultStats'}).text
    if not s:
        return 0
    m = re.search(r'([0-9,]+)', s)
    return int(m.groups()[0].replace(',', ''))