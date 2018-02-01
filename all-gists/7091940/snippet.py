import json
import luigi
import luigi.hdfs
import luigi.hadoop
import pandas as pd

import numpy
import pandas
luigi.hadoop.attach(numpy, pandas)

class InputText(luigi.ExternalTask):
    part = luigi.IntParameter()

    def output(self):
        return luigi.LocalTarget('%i.tdf' % self.part)


class GenerateJSON(luigi.Task):

    def requires(self):
        return [InputText(part) for part in range(10)]

    def output(self):
        return luigi.hdfs.HdfsTarget('data.json')

    def run(self):
        f = self.output().open('w')
        for file in self.input():
            df = pd.read_table(file.open('r'), nrows=5)
            for index, row in df.iterrows():
                f.write("%s\n" % row.to_json())

        # output data
        f.close()


class NumberOfWords(luigi.hadoop.JobTask):

    def requires(self):
        return GenerateJSON()

    def output(self):
        return luigi.hdfs.HdfsTarget('number_of_words')

    def mapper(self, line):
        line = json.loads(line)
        wc = line['word_count']
        yield 'word', wc if wc is not None else 0

    def reducer(self, key, values):
        yield key, sum(values)

if __name__ == '__main__':
    luigi.run()
