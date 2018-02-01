import pandas
df = pandas.read_csv('offers.csv.gz', compression='gzip')
categories = df.category.tolist()

subset = open('subset.csv', 'w')
fl = open('transactions.csv', 'r')
fl.readline()
while True:
    l = fl.readline()
    if l == '':
        break
    
    if numpy.int64(l.split(',')[3]) in categories:
        subset.write(l)