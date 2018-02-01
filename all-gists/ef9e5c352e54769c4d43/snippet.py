import requests
from bs4 import BeautifulSoup as bs
from itertools import chain, filterfalse


langs = {'python': ['(py)', '(pypy)', '(py3)'],
         'ruby': ['(rb)']}


def get_pids(maxpage=17):
    """ gatter problem ids and return it one by one """
    baseurl = 'https://algospot.com/judge/problem/list/%d'
    for pagenum in range(1, maxpage+1):
        page = requests.get(baseurl % pagenum, timeout=None)
        soup = bs(page.text)
        tds = soup.find_all('td', class_='id')
        for p in tds:
            yield p.find('a').text.strip()


def solved_with(lang):
    """ return  a filter that checks if provided problem is ever solved with the
    language or not
    """
    if lang not in langs:
        raise
    target = langs[lang]
    baseurl = 'https://algospot.com/judge/problem/stat/%(pid)s/%(page)d/'

    def f(pid):
        firstpage = requests.get(baseurl % {'pid': pid, 'page': 1})
        soup = bs(firstpage.text)
        maxpage = soup.find('span', class_='step-links').find_all('a')[-1].text
        for pagenum in range(1, int(maxpage)+1):
            page = requests.get(baseurl % {'pid': pid, 'page': pagenum})
            soup = bs(page.text)
            tds = chain(soup.find_all('td', class_='fastest'),
                        soup.find_all('td', class_='shortest'))
            ans = ''.join(td.text for td in tds)
            if any(t in ans for t in target):
                return True
        return False

    return f


def solved_by(uid):
    """ return a filter that checks if provided problem is ever solved by the
    user or not. user is specified by user id, shown in his profile page url.
    for example user fleo0917(https://algospot.com/user/profile/13227)'s user
    id is '13227'
    """
    solved = set()
    baseurl = 'https://algospot.com/judge/problem/list/%(page)d?verdict=solved&user_tried=%(uid)s'
    firstpage = requests.get(baseurl % {'uid': uid, 'page': 1})
    soup = bs(firstpage.text)
    maxpage = soup.find('span', class_='step-links').find_all('a')[-1].text
    for pagenum in range(1, int(maxpage)+1):
        page = requests.get(baseurl % {'uid': uid, 'page': pagenum})
        soup = bs(page.text)
        tds = soup.find_all('td', class_='id')
        for p in tds:
            solved.add(p.find('a').text.strip())

    def f(pid):
        return pid in solved

    return f


def gen_url(pid):
    """ return problem definition url """
    return 'https://algospot.com/judge/problem/read/%s' % pid


if __name__ == '__main__':
    probs = get_pids()
    probs = filter(solved_with('python'), probs)
    probs = filterfalse(solved_by('13227'), probs)
    for p in probs:
        print('[%s](%s)' % (p, gen_url(p)))