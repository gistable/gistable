"""Extract the first page of all NIPS papers and combine them in one PDF file

:author: Davide Zilli
:date:  03 Dec 2017
:lastedit: 03 Dec 2017
"""

import os
import requests
from PyPDF2 import PdfFileWriter, PdfFileReader
from bs4 import BeautifulSoup
from io import BytesIO


NIPS = "https://papers.nips.cc"
proceedings_url = NIPS + "/book/advances-in-neural-information-processing-systems-30-2017"
papers_dir = "/tmp/NIPS2017/papers"
proceedings_page_path = os.path.join(papers_dir, "proceedings.html")
abstracts_filename = os.path.join(papers_dir, "NIPS2017-abstracts.pdf")


def get_page(url: str, path: str) -> BeautifulSoup:
    """Get a web page and store it, or load it from disk if present"""
    if os.path.exists(path):
        with open(path) as p:
            page = p.read()
    else:
        page = requests.get(url).text
        with open(path, 'w') as p:
            p.write(page)
    return BeautifulSoup(page)


def get_pdf(url: str, path: str) -> PdfFileReader:
    """Get a PDF from the web and store it, or load it from disk if present"""
    if os.path.exists(path):
        reader = PdfFileReader(path)
    else:
        pdf = requests.get(url)
        reader = PdfFileReader(BytesIO(pdf.content))
        writer = PdfFileWriter()
        writer.appendPagesFromReader(reader)
        with open(path, 'wb') as p:
            writer.write(p)

    return reader


def extract() -> None:
    """Extract and combine the first page of all proceedings' PDFs into one"""

    if not os.path.exists(papers_dir):
        os.makedirs(papers_dir)

    proceedings_soup = get_page(proceedings_url, proceedings_page_path)

    paper_links = proceedings_soup.find_all("a")
    print("found {} links".format(len(paper_links)))

    scanned = 0
    errors = []
    with open(abstracts_filename, "wb") as abstracts_pdf:
        writer = PdfFileWriter()
        for link in paper_links:
            if link["href"].startswith("/paper/"):
                try:
                    scanned += 1
                    print("\n*** [{:d}] paper page found".format(scanned))
                    print(link["href"])

                    paper_soup = get_page(NIPS + link["href"], os.path.join(papers_dir, os.path.basename(link["href"])))

                    pdf_links = paper_soup.find_all("a")
                    pdf_a_link = next(filter(lambda x: x.text == "[PDF]", pdf_links))
                    pdf_link = pdf_a_link["href"]
                    print("found PDF link:", pdf_link)

                    pdf = get_pdf(NIPS + pdf_link, os.path.join(papers_dir, os.path.basename(pdf_link)))
                    writer.addPage(pdf.getPage(0))

                    print("Added paper '{}'".format(paper_soup.find_all("h2", attrs={"class": "subtitle"})[0].text))
                except (MemoryError, KeyboardInterrupt):
                    break
                except Exception as e:
                    print("Failed to add paper: '{}' ({})".format(link["href"], e))
                    errors.append(link["href"])
        writer.write(abstracts_pdf)

    print("\nerrors:\n", errors)
    print("output in '{}'".format(abstracts_filename))


if __name__ == '__main__':
    extract()
