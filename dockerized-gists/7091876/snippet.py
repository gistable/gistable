import re
import json
import luigi
import pandas as pd
from mysolr import Solr
from bs4 import BeautifulSoup


class InputText(luigi.ExternalTask):

    def output(self):
        return luigi.LocalTarget('html.tdf')


class CleanHTML(luigi.Task):

    def requires(self):
        return InputText()

    def output(self):
        return luigi.LocalTarget('text.tdf')

    def run(self):
        df = pd.read_csv(self.input().open('r'), sep='\t')
        df = df[df['content'].notnull()]

        def clean(x):
            x = re.sub(r'<br>', r'<br>\n', x)
            x = re.sub(r'<br />', r'<br>\n', x)
            x = re.sub(r'<br/>', r'<br>\n', x)
            x = re.sub(r'<p>', r'\n<p>', x)
            x = re.sub(r'</p>', r'</p>\n', x)
            return BeautifulSoup(x, 'html.parser').getText(' ')

        df['text'] = df['content'].apply(clean)

        # output data
        f = self.output().open('w')
        df.to_csv(f, sep='\t', encoding='utf-8', index=None)
        f.close()


class SolrIndex(luigi.Task):

    def requires(self):
        return CleanHTML()

    def run(self):
        df = pd.read_csv(self.input().open('r'), sep='\t')
        df['id'] = df['url']

        solr = Solr('SOLR_HOST')

        # Index 10 docs at a time
        start = 0
        increment = 10
        while len(df[start:start+increment]) > 0:
            sliced = df[start:start+increment]
            docs = []
            for index, row in sliced.iterrows():
                doc = json.loads(row.to_json())
                docs.append(doc)

            solr.update(docs, 'json')
            if start % 1000 == 0:
                # Just to see that is working
                print start
            start += increment


if __name__ == '__main__':
    luigi.run()
    # luigi.run(main_task_cls=CleanHTML)
    # luigi.run(main_task_cls=SolrIndex)
