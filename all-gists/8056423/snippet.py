class lazy_csv_reader(list):
    def __init__(self, csv_reader, pos):
        self.reader = csv_reader
        self.pos = pos
        
    def __iter__(self):
        r = self.reader.next()
        while r:
            yield r[self.pos]
            r = self.reader.next()

# Example:

# Suppose you have a big CSV with a few columns, and 
# you want to TF-IDF vectorize the second column.
# You can do this with csv.DictReader but it is slower
# due to the parsing. So I would recommend using csv.reader
# instead.

# import csv
# from sklearn import feature_extraction
# r = csv.reader(open('big.csv', 'rb'))
# r.next() # get rid of the header
# tfidf_vec = feature_extraction.text.TfidfVectorizer()
# tfidf = tfidf_vec.fit_transform(lazy_csv_reader(r, 1))