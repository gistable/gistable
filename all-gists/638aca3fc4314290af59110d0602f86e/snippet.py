#!/usr/bin/python3.5
import concurrent.futures
import logging
import re
import urllib.parse

import requests

logging.basicConfig(level=logging.INFO)

WIKTIONARY_URL = 'https://en.wiktionary.org/wiki/'
_IPA_REGEX = re.compile('IPA<[\s\w<>=\"-:?@.;()%!\[\]|]+?>key</a>\)</sup>:[^>]+>([^<]+)<')
_WORD_LIST_REGEX = re.compile('li><a href="([^"]+)" title="([^"]+)"')  # Probably want to use a DOM parser for this

# TODO Consider using the offline dump from wiktionary/using the wiktionary API
# TODO see this stackoverflow: http://stackoverflow.com/questions/2770547/how-to-retrieve-wiktionary-word-content


def list_ipa_for_word(url):
    """! get list of the individual word and their ipa.
    """
    return _IPA_REGEX.findall(scrape_url(url))


def scrape_words(url):
    """! Get the words and the url.

    TODO urlencode if the words can only be able to make the url, save memory!!
    """
    return _WORD_LIST_REGEX.findall(scrape_url('{}{}'.format(WIKTIONARY_URL, url)))  # ('/wiki/zhvishem', 'zhvishem')


def scrape_url(url):
    """
    TODO https://en.wiktionary.org/wiki/baba#Albanian
    scrap only the bookmark if present
    """
    if not url.startswith(WIKTIONARY_URL):
        url = urllib.parse.urljoin(WIKTIONARY_URL, url)
    logging.debug('Retrieving: <{}>'.format(url))
    return requests.get(url).text


def _local_word_list(maxwords=None):
    # We can use the wikimedia dump from this webpage instead
    # https://dumps.wikimedia.org/enwiktionary/latest/
    with open('/usr/share/dict/american-english', 'r') as word_dictionary:
        for index, word in enumerate(word_dictionary):
            yield word.strip()
            if index == maxwords:
                return


def _word_list(language):
    return (word for url, word in scrape_words(language))


def serially_download_words(language):
    logging.info('Serially downloading word list')
    for word in _word_list(language):
        logging.info('{} found: {}'.format(word, scrape_words(word)))
    logging.info('Finished serially downloading word list')


def concurrently_download_words(language):
    logging.info('Concurrently downloading word list')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures_to_words = {executor.submit(scrape_words, words): words for words in _word_list(language)}
        for future in concurrent.futures.as_completed(futures_to_words):
            word = futures_to_words[future]
            logging.info('Parsing: <{}>'.format(word))
            try:
                word_data = future.result()
                logging.info('<{}> found: {}'.format(word, word_data))
            except Exception as exc:
                logging.exception('{!r} generated an exception: {!s}'.format(word, exc))
            else:
                logging.info('Finished parsing: <{}>'.format(word))
    logging.info('***Finished Parsing all words***')


if __name__ == '__main__':
    # serially_download_words()
    concurrently_download_words(language='Index:Albanian')
