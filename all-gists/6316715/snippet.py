from luigi.format import Format
import csvkit

class CSVOutputProcessor(object):
    """
    A simple CSV output processor to be hooked into Format's
    `pipe_writer`. 

    If `cols` are given, the names are used as CSV header, otherwise no
    explicit header is written.
    """
    def __init__(self, output_pipe, delimiter='\t', encoding='utf-8', cols=None):
        self.writer = csvkit.CSVKitWriter(output_pipe, delimiter=delimiter,
                                                       encoding=encoding)
        self.output_pipe = output_pipe
        self.cols = cols
        if cols:
            # write header
            self.writer.writerow(cols)

    def write(self, *args, **kwargs):
        if self.cols and not len(args) == len(self.cols):
            raise RuntimeError('This format expects %s columns: %s, got %s.' % (
                               (len(self.cols), self.cols, len(args))))
        self.writer.writerow(args)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type:
            # pass on the exception; it get's handled in `atomic_file`: 
            # http://git.io/x7EVtQ
            return False
        self.output_pipe.close()


class CSVInputProcessor(object):
    """
    A simple CSV output processor to be hooked into Format's
    `pipe_reader`.

    If `cols` are given, this processor will turn each row in the file into
    a `namedtuple` with the attributes given in cols. Otherwise just return
    the row as tuple.
    """
    def __init__(self, input_pipe, encoding='utf-8', delimiter='\t', cols=None):
        self.reader = csvkit.CSVKitReader(input_pipe, encoding=encoding,
                                                      delimiter=delimiter)
        self.input_pipe = input_pipe
        self.cols = cols
        if cols:
            header = self.reader.next() # consume the header
            if not tuple(header) == tuple(cols):
                raise RuntimeError('Format mismatch, expected: %s, but got: %s' % 
                                   (cols, header))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.input_pipe.close()

    def __iter__(self):
        if self.cols:
            Row = collections.namedtuple('Row', self.cols)
            for line in self.reader:
                yield Row(*line)
        else:
            for line in self.reader:
                yield tuple(line)


class CSVFormat(Format):
    """
    Helper for reading from and writing to CSV files.

    Explicit column names can be given via `cols`. The headers are written
    to the file or read and checked against the actual header row. If `cols`
    are `None` no header is written and the reader will just return a tuple.
    """
    def __init__(self, delimiter='\t', encoding='utf-8', cols=None):
        self.delimiter = delimiter
        self.encoding = encoding
        self.cols = cols
        if cols:
            if not len(cols) == len(set(cols)):
                raise ValueError('Column names must be uniq.')
            if not isinstance(cols, (list, tuple)):
                raise ValueError('Column names (headers) must be given as '
                                 'list or tuple.')


    def pipe_reader(self, input_pipe):
        return CSVInputProcessor(input_pipe, delimiter=self.delimiter,
                                             encoding=self.encoding,
                                             cols=self.cols)

    def pipe_writer(self, output_pipe):
        return CSVOutputProcessor(output_pipe, delimiter=self.delimiter,
                                               encoding=self.encoding,
                                               cols=self.cols)

# CSV format needs to be instantiated (in contrast to, e.g. Gzip) and takes
# kwargs for `delimiter`, `encoding` and column names as `cols`.

# Example: plain CSV
CSV = CSVFormat()

# Example: plain TSV without headers
TSV = CSVFormat(delimiter='\t')

# Example: TSV with column names, delimiter and encoding
Custom = CSVFormat(delimiter=':', encoding='latin-1', 
                   cols=('name', 'state', 'zipcode'))


class CSVWriterExample(luigi.Task):
    """ 
    Example task writing data as TSV.
    Will write the following to a file:

        $ cat example.tsv
        name    state   zipcode
        John    CA  92101
        Jane    NY  10304
        Jazz    TX  78701    
    """
    def run(self):
        with self.output().open('w') as output:
            output.write('John', 'CA', 92101)
            output.write('Jane', 'NY', 10304)
            output.write('Jazz', 'TX', 78701)
            # would yield an error, since explicit column names were given
            # and those are expected to be present
            # output.write('Hello', 'world')

    def output(self):
        return luigi.LocalTarget('./example.tsv', 
                                 format=CSVFormat(delimiter='\t', 
                                 cols=('name', 'state', 'zipcode')))


class CSVReaderExample(luigi.Task):
    """ Example task reading data from local file with given CSV format.
    """
    def requires(self):
        return CSVWriterExample()

    def run(self):
        with self.input().open() as handle:
            for row in handle:
                # make use of the namedtuple ...
                print('%s from %s %s' % (row.name, row.zipcode, row.state))
                # ... or just the tuple
                print('Hi %s' % row[0])

    def complete(self):
        return False
