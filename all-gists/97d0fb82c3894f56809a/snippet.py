from urllib.request import urlretrieve
from time import sleep

import requests
from bs4 import BeautifulSoup as bs


def get_files():
    """ Gets files of specified extension through user input
    from a specified full URL path; downloads each file to
    the user's specified local directory. """

    while True:
        url = input("Enter the URL you want to scrape from: ")

        suffix = input("What type of file do you want to scrape? \nExamples: .png, .pdf, .doc - ")

        filepath = input("Specify a file path to save to: ")

        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url

        response = requests.get(url, stream=True)
        soup = bs(response.text)

        link_list = [link.get('href') for link in soup.find_all('a') if suffix in str(link)]
        
        for link in link_list:
            file_name = link.rpartition('/')[-1]
            urlretrieve(url.rsplit('/', 1)[0] + '/' + link, filepath + '\\' + file_name)

        print_message(link_list, suffix)
        if not repeat(input("Scrape from another URL? ")):
            break


def print_message(lst, suffix):
    """ Notifies user when done downloading files OR
    if there are no files of the type they specified
    Input: List of file names, String for file extension """
    if lst:
        print("Finished. Downloaded all files of type", suffix)
    else:
        print("No files of type", suffix, "were found.")


def repeat(decision):
    """ Function for running the file scraper again
    Input: String 'yes' or 'no' """

    if decision.lower().startswith("y"):
        return True

    print("Closing program...")
    sleep(3)
    print("Goodbye")
    return False

if __name__ == '__main__':
    get_files()