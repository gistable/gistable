import requests
import re
import time
import webbrowser

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2"}
lastnum = 85


def chk_new_post():
    global headers, lastnum
    data = requests.get("https://www.kitribob.kr/board/1", headers=headers).text
    count = re.findall(r"list_obj\.init\(\{\"total_cnt\":\"([0-9]+)\"", data)[0]
    
    if int(count) > lastnum:
        postnum = re.findall(r"\[\{\"board_no\":\"([0-9]+)\"",data)[0]
        url = "https://www.kitribob.kr/board/detail/1/{}".format(postnum)
        webbrowser.open_new(url)
        return True


while True:
    if chk_new_post():
        print("BoB new post found")
    time.sleep(10)
