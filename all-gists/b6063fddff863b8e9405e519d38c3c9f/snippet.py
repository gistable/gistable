import requests


def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


if __name__ == '__main__':
    page = get_web_page('https://www.ptt.cc/bbs/Beauty/index.html')
    if page:
        print(page)