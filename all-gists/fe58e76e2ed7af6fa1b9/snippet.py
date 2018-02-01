#!/usr/bin/env python

import bs4
import requests
import time



def main():
    for sido_idx in range(1,18):
        sido = str(sido_idx).zfill(2)
        gugun_idx = 0
        goto_sido = False
        while True:
            if goto_sido is True:
                break
            gugun_idx += 1
            gugun = str(gugun_idx).zfill(2)
            page_idx = -1
            while True:
                time.sleep(2)
                page_idx += 1
                r = requests.post("http://www.istarbucks.co.kr/Store/store_search2.asp",
                        {"sido" : sido, "gugun": sido + gugun, "PageNo": str(page_idx)})
                b = bs4.BeautifulSoup(r.text)
                items = b.find_all("ul",class_="storeSeachList")[0].find_all("ul")
                if len(items) == 0:
                    if page_idx == 0:
                        goto_sido = True
                    break
                for item in items:
                    addr = item.find_all("li")[1].text
                    open("starbucks.text",'a').write(addr.encode("utf8") + "\n")





if __name__ == '__main__':
    main()

