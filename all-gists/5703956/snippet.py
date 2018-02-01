#! /usr/bin/env python
# coding=utf-8
__author__ = 'Kingson zhou'
import requests
import os
import time
from bs4 import BeautifulSoup
import random
"""
说明：
1.此脚本是用来下载“读远”（http://www.readfar.com/）上的电子书，以防备突然被关站。
2.本脚本主要使用requests库、BeautifulSoup库以及random函数
3.脚本中的Cookie和add_comments函数中的authenticity_token值和当前登录用户有关，需要自行替换
"""

header = {"User-Agent": "Mozilla/5.0(Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1)\
# Gecko/20090624 Firefox/3.5", "Cookie": "angle_session=BAh7CEkiD3Nlc3Npb25faWQGOgZFRkkiJWEyOTAzODA0ZmNhNWY1NDdjZmRiMDY1ZTk1NTAyZGQ2BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMVFheUs4cW85d1AzS1diVkIwVFM0OXVDcmZsQWVDajVDaW1nQlNkV3VtQlE9BjsARkkiDHVzZXJfaWQGOwBGVToaTW9wZWQ6OkJTT046Ok9iamVjdElkIhFRq%2FXegr6cG7QAAAI%3D--6bd72d49961e0a563077b14992ab80536cd4d98c; remember_token=51abf5de82be9c1bb4000002%24a0564e924a2ccdf23b052ecbf60e8dbbf784472a90b3888fe5d0d447ef3ad4f4; _ga=1.2.616581869.1370224027; Hm_lvt_866bd67df0812fb6fba5538f31acc23b=1370224027; Hm_lpvt_866bd67df0812fb6fba5538f31acc23b=1370236606"}


main_url = 'http://www.readfar.com'
msg = ['正在看，还可以', '一本非常不错的书，值得大家阅读。', '正在找这本书，谢谢', '谢谢分享']


def save(bookename):
    if os.path.exists(bookename) is False:
        os.mkdir(bookename)
        return True
    else:
        return False


def add_comments(book_list_url):
    """
    由于下载电子书，需要消耗karma，大概1M需耗费1karma，如需要大量下载，
    还需提前通过给书籍添加评论来储备karma，自认为不太道德，造成垃圾评论之嫌，望站长见谅
    """
    get_book_list_url_request = requests.get(book_list_url)
    main_soup = BeautifulSoup(get_book_list_url_request.content)
    book_list_url_tag = main_soup.find_all("a", attrs={"class": "book thumbnail"})
    for book_url in book_list_url_tag:
            book_name = book_url.find('h4').string
            book_url = book_url["href"]
            get_book_details_request = requests.get(
                book_url, headers=header)
            main_soup = BeautifulSoup(get_book_details_request.content)
            book_comments_url = main_soup.find(
                "form", attrs={"class": "new_comment"})
            # for book_comments_url in book_comments_url_tag:
            book_comments_url = main_url + book_comments_url["action"]
            payload = {"utf8": "✓",
                       "authenticity_token": *****, #与当前登录用户有关，需要自己抓包分析
                       "comment[content]": random.choice(msg),
                       "commit": "确定",
                       "sync": 0}

            add_book_comments = requests.post(
                book_comments_url, data=payload, headers=header)
            if add_book_comments.status_code == 200:
                print book_name, "评论添加成功"
            else:
                print book_name, "评论添加失败"
            time.sleep(10)


def download_book(book_list_url):
    """
    从给定的List页面中找到进入每本书的详情页面的URL，再在详情页面中找到下载的地址，进行下载即可
    """
    while book_list_url is not False:
        get_book_list_url_request = requests.get(book_list_url)
        main_soup = BeautifulSoup(get_book_list_url_request.content)
        book_list_url_tag = main_soup.find_all("a", attrs={"class": "book thumbnail"})
        for book_url in book_list_url_tag:
            book_name = book_url.find('h4').string
            book_url = book_url["href"]
            get_book_details_request = requests.get(book_url)
            book_details_soup = BeautifulSoup(get_book_details_request.content)
            book_details_tag = book_details_soup.find_all(
                "a", attrs={"data-toggle": "tooltip"})
            for book_download_url in book_details_tag:
                book_formart = book_download_url["class"][0]
                book_download_url = book_download_url["href"]
                if save(book_name) is False:
                    break
                else:
                    book_download_url = main_url + book_download_url
                    book_download_request = requests.get(
                        book_download_url, headers=header)
                    with open(book_name + "/" + book_name + "." + book_formart, "wb") as code:
                        code.write(book_download_request.content)
                    print book_name, book_download_url, "Download Done."
                    time.sleep(10)
        try:
            get_book_list_url_request = requests.get(book_list_url)
            main_soup = BeautifulSoup(get_book_list_url_request.content)
            book_next_url_tag = main_soup.find("li", attrs={"class": "next"})
            book_list_url = book_next_url_tag.find('a')['href']
        except Exception:
            print "Download Success!"
            break

if __name__ == '__main__':
    book_list_url = 'http://www.readfar.com/books/best?sort=update'
    download_book(book_list_url)
#    add_comments("http://www.readfar.com/books?p=57")
