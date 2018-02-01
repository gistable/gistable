from itertools import izip
import re

output_file = 'dataset.csv'
input_files = {
    'train/X_train.txt': 'train/y_train.txt', 
    'test/X_test.txt': 'test/y_test.txt'
}

def getOutputLines(filenames):
    for X,y in filenames.iteritems():
        with open(X) as Xf, open(y) as yf:
            for Xline, yline in izip(Xf, yf):
                Xline = re.sub(' +', ' ', Xline).strip() #remove multiple white spaces and strip
                yield ','.join([yline.strip()] + Xline.split(' ')) + "\n" #concat in csv format
                


with open(output_file, 'w+') as f:
    for newline in getOutputLines(input_files):
        f.writelines(newline)
