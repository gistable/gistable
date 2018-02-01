#!usr/bin/env python
# coding: utf-8

import time
import requests
import BeautifulSoup

QQ = 'username'
password = r'password'
refresh_time = 5

user_agent = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 820)'
headers = { 'user-agent': user_agent }

def like(url):
    response = requests.get(url, headers=headers).text
    if response.find(u'成功') != -1:
        return True

def find_like(html):
    soup = BeautifulSoup.BeautifulSoup(html)
    links = soup.findAll('a')
    for index, link in enumerate(links):
        if link.text.startswith(u'赞(') and link['href'].find('like_action.jsp') != -1:
            like_url = link['href']
            if like(like_url):
                for i in range(index - 1, -1, -1):
                    l = links[i]
                    if l['href'].find('blog.jsp?B_UID') != -1:
                        print "Successfully liked %s's post. [%s]" % (l.text, time.asctime())
                        break



def login():
    print 'Logining...'

    response = requests.get('http://ish.z.qq.com/feeds_friends.jsp').text
    start = response.find('http://pt.3g.qq.com/s?')
    end = response.find('"', start)
    login_url = response[start:end]

    response = requests.get(login_url, headers=headers).text
    start = response.find('http://pt.3g.qq.com/')
    end = response.find('"', start)
    post_url = response[start:end]

    data = {
        'qq': QQ,
        'pwd': password,
        'login_url': login_url,
        'go_url': 'http://ish.z.qq.com/feeds_friends.jsp',
        'sid_type': '1',
        'aid': 'nLoginqz'
    }
    response = requests.post(post_url, data=data, headers=headers)
    return response.url + '&type=all'

def main():
    url = login()
    while True:
        response = requests.get(url).text
        if response.find(u'很抱歉，您访问的内容因系统繁忙暂时无法读取，您可以') != -1:
            continue
        elif response.find(u'好友动态') != -1:
            find_like(response)
        else:
            url = login()
        time.sleep(refresh_time)

if __name__ == '__main__':
    main()
