"""Collect article metadata and associate it with url dimension.

Currently the url dimension includes a domain and url, but there is
a higher level grouping that we care about. What is the outlet,
who authored the article, what kind of site is it, when was
it published, etc.

"""

import os
import datetime
import asyncio
import aiohttp
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from newspaper import Article, Config

import logging
logger = logging.getLogger(__name__)

articles = []
fields = ['title', 'author', 'top_image', 'site_name', 'site_type',
          'category', 'sub_category', 'page_type', 'sub_page_type']

# configuration for Newspaper to minimize processing time
config = Config()
config.fetch_images = False


class ExternalArticle(Article):
    """Represents an article that referred traffic to the site."""
    def __init__(self, url, config=config, **kwargs):
        super().__init__(url, config=config, **kwargs)

    def process(self):
        self.download()
        self.parse()
        self.nlp()

    @property
    def site_name(self):
        if self.meta_data['og']:
            return self._sanitize(self.meta_data['og']['site_name'])
        else:
            return ''

    @property
    def site_type(self):
        if self.meta_data['og']:
            return self._sanitize(self.meta_data['og']['type'])
        else:
            return ''

    @property
    def category(self):
        return self._sanitize(self.meta_data.get('category', ''))

    @property
    def sub_category(self):
        return self._sanitize(self.meta_data.get('subcategory', ''))

    @property
    def page_type(self):
        return self._sanitize(self.meta_data.get('pagetype', ''))

    @property
    def sub_page_type(self):
        return self._sanitize(self.meta_data.get('subpagetype', ''))

    @property
    def author(self):
        if len(self.authors) > 0:
            return self.authors[0]
        else:
            return ''

    @staticmethod
    def _sanitize(value):
        value = value.replace(',', '')
        value = value.replace('"', '')
        return value


def append_to_csv(df, path, sep=","):
    """Append the provided dataframe to an existing one, else writes as new."""
    if not os.path.isfile(path):
        df.to_csv(path, mode='a', index=False, sep=sep)
    else:
        df.to_csv(path, mode='a', index=False, sep=sep, header=False)


@asyncio.coroutine
def get_article_body(article):
    """Collect the article and parse the body."""
    print('downloading: %s' % article.url)
    response = yield from aiohttp.request('GET', article.url)
    body = yield from response.read()
    return body


def setup_article(article):
    """Perform computationally heavy tasks of article parsing and nlp."""
    print('parsing: %s' % article.url)
    article.parse()
    print('processing: %s' % article.url)
    article.nlp()
    return article


@asyncio.coroutine
def add_article_attributes(row):
    """Initialize article from row and add attributes to row."""
    try:
        a = ExternalArticle(row['url'])

        # throttle total number of simultaneous requests
        with (yield from semaphore):
            body = yield from get_article_body(a)
            a.set_html(body)

        # run article processing in subprocess
        a = yield from loop.run_in_executor(p, setup_article, a)

        print(a.title)
        print('')

        for field in fields:
            row[field] = getattr(a, field)

    # ToDo: handle exception in a better way, for now don't stop processing
    except Exception as e:
        print(e)

    articles.append(row)


@asyncio.coroutine
def process_rows():
    """Watch for a batch of rows to be processed and write to csv.

    ToDo: Detect when processing is complete, otherwise runs until interrupted
    """
    while True:
        batch = []
        while len(batch) < 500:
            if len(articles) > 0:
                yield batch.append(articles.pop())
            else:
                yield

        df_batch = pd.DataFrame.from_records(batch, columns=df.columns.tolist())
        append_to_csv(df_batch, './output/processed_article_urls.tsv', sep='\t')


# retrieve and initialize data structure of urls
df = pd.read_csv('./output/processed_possible_urls.csv')
df = df.ix[df.outlet_key > 0, :]
for field in fields:
    df[field] = ''
df['publish_date'] = datetime.date(year=1900, month=1, day=1)

# collect lists of tuples of values
links = df.drop_duplicates()
links = links.to_records(index=False)

# create pool of processes to perform cpu bound work
p = ProcessPoolExecutor(8)

# setup semaphore to limit network bound work
semaphore = asyncio.Semaphore(100)

# create coroutines to perform the work
tasks = [add_article_attributes(link) for link in links]
tasks = [process_rows()] + tasks

# start the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
