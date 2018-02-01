import requests
import datetime
from BeautifulSoup import BeautifulSoup
import random
import time

def get_page(url):
    r=requests.get(url)
    print url
    return BeautifulSoup(r.text)


def dig_member(dom):
    members = []
    content = dom.body.contents[3].contents[1].contents[5].contents[7]
    for div in content.contents:
        try:
            if div["class"]=="cell":
                member = div.table.tr.contents[5].strong.a.text
                members.append(member)
        except:
            pass
    return members

def get_member():
    base_url="http://v2ex.com/t/94363?p="
    members = []
    for pid in xrange(100):
        url = base_url+str(pid+1)
        dom = get_page(url)
        for member in dig_member(dom):
            members.append(member)
            print member
    time.sleep(30)
    return list(set(members))

def main():
    members = get_member()
    random.shuffle(members)
    select_idx = random.randint(0,len(members)-1)
    print "execued at %s"%datetime.datetime.now()
    print "the winner is %s"%members[select_idx]

if __name__ == "__main__":
    main()