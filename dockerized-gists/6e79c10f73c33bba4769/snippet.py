#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import requests

from bs4 import BeautifulSoup as bs


ROOT_URL = "http://link.springer.com"
OUTPUT_DIR = "/tmp/springer_dump"


def walk_pages(number_of_pages):
    for page_number in range(1, number_of_pages + 1):
        search_url = "{0}{1}{2}{3}{4}".format(
            ROOT_URL,
            "/search/page/",
            repr(page_number),
            "?showAll=false&facet-language=%22En%22",
            "&facet-content-type=%22Book%22&sortOrder=newestFirst"
        )
        print("=== Crawling content for page {} ===".format(
            search_url
        ))
        page_data = requests.get(search_url)

        if page_data.status_code != 200:
            print("unable to retrieve content for page {}".format(
                search_url
            ))
            quit()
        page_content = bs(page_data.content, "html.parser")

        page_links = get_book_links(page_content)

        download_links = get_pdf_links(page_links)

        download_pdfs(download_links)


def make_tmp_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def get_book_links(bs_content):
    return bs_content.find_all("a", class_="title")


def get_pdf_links(bs_content):
    return ["{}{}".format(ROOT_URL, link.get("href")) for link in bs_content]


def download_pdfs(urls):
    for url in urls:
        page_data_ = requests.get(url)

        if page_data_.status_code != 200:
            quit()

        page_content_ = bs(page_data_.content, "html.parser")
        book_name = page_content_.find("span", class_="pissn").get_text().split()[0]
        book_url = "{}{}".format(
            ROOT_URL,
            page_content_.find("a", class_="webtrekk-track").get("href")
        )
        pdf_path = "{}{}{}{}".format(
            OUTPUT_DIR,
            "/",
            book_name,
            ".pdf"
        )
        with open(pdf_path, "wb+") as pdf_file:
            pdf_ = requests.get(book_url)

            if pdf_.status_code != 200:
                quit()

            pdf_file.write(pdf_.content)

        print(book_name + " : done")


def main():
    search_url = "{0}{1}{2}".format(
        ROOT_URL,
        "/search/page/1?showAll=false&facet-language=%22En%22",
        "&facet-content-type=%22Book%22&sortOrder=newestFirst"
    )
    first_page = requests.get(search_url)
    if first_page.status_code != 200:
        quit()
    first_page = bs(first_page.content, "html.parser")
    page_number = first_page.find("span", class_="number-of-pages").get_text()
    make_tmp_dir()
    walk_pages(int(page_number))


if __name__ == '__main__':
    main()
