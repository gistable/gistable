"""Computes the arXiv usage rates as a function of journal.

This is a rough script used for the sake of providing the numbers for one tweet:
https://twitter.com/GeertHub/status/705788341531201537

I may turn this into a webservice that reports on the use of arXiv every month?
What do you think?
"""
import ads
import json
import os

CACHEDIR = 'cache'

ADS_FIELDS = ['date', 'pub', 'id', 'volume', 'doi', 'citation_count', 'year', 'identifier',
              'alternate_bibcode', 'arxiv_class', 'bibcode',
              'first_author_norm', 'pubdate', 'title',
              'property', 'author', 'email', 'orcid',
              'author_norm', 'page', 'first_author',
              'read_count', 'issue', 'aff']

JOURNALS = ['Icarus',
            'Monthly Notices of the Royal Astronomical Society',
            'The Astrophysical Journal',
            'The Astronomical Journal',
            'Astronomy and Astrophysics',
            'Earth Moon and Planets',
            'Publications of the Astronomical Society of the Pacific',
            'Planetary and Space Science',
            'Journal of Geophysical Research'
            ]


class JournalJudge(object):

    def __init__(self, journal, month, use_cache=True):
        self.journal = journal
        self.month = month
        self._articles = None
        self._cache_fn = os.path.join(CACHEDIR, '{}-{}.json'.format(journal.replace(' ', '-'), month))
        if use_cache and os.path.exists(self._cache_fn):
            print('Using cached data from {}'.format(self._cache_fn))
            self._articles = json.load(open(self._cache_fn))
        else:
            self._articles = self._retrieve_articles()
            self.save_cache()

    @property
    def articles(self):
        return self._articles

    def _retrieve_articles(self):
        """Retrieves all the articles for a journal/month combination from ADS.

        Returns a list of `ads.Article` objects.
        """
        qrystring = 'pub:"{}" pubdate:"{}"'.format(self.journal, self.month)
        # At the time of writing, `ads` would break if rows > 2000
        result = ads.SearchQuery(q=qrystring, fl=ADS_FIELDS, rows=2000, max_pages=1000)
        return [article._raw for article in result]

    def save_cache(self):
        self.to_json(self._cache_fn)

    def to_json(self, output_fn):
        json.dump(self.articles, open(output_fn, 'w'), indent=True)

    def has_preprint(self, article):
        if any(['arxiv' in artid.lower() for artid in article['identifier']]):
            return True
        return False

    def count_preprints(self):
        return(sum([self.has_preprint(art) for art in self.articles]))

    def print_summary(self):
        print('Summary for {}/{}:'.format(self.journal, self.month))
        n_articles = len(self.articles)
        n_preprints = self.count_preprints()
        fraction = 100 * n_preprints / n_articles
        print('Articles: {}'.format(n_articles))
        print('Preprints: {}'.format(n_preprints))
        print('Score: {:.0f}%'.format(fraction))

    def print_articles(self):
        print('Are on arXiv:')
        for article in self.articles:
            if self.has_preprint(article):
                print(article['first_author'])
                print(article['aff'][0])
                print(article['title'][0])

        print('Are not on arXiv:')
        for article in self.articles:
            if not self.has_preprint(article):
                print(article['first_author'])
                print(article['aff'][0])
                print(article['title'][0])

    def print_nonpreprint_articles(self):
        out = open('2015-apj-papers-not-on-arxiv.txt', 'w')
        for article in self.articles:
            if not self.has_preprint(article):
                out.write('{} {}\n'.format(article['bibcode'], article['title'][0]))
        out.close()


if __name__ == '__main__':
    for journal in JOURNALS:
        jj = JournalJudge(journal, '2015')
        jj.print_summary()
