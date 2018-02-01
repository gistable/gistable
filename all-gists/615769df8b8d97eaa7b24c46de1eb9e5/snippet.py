import re
import glob

def main():
    outputFile = 'output.tsv'
    files = glob.glob('*.html')

    print "Extracting from %s files" %(len(files))

    data = []
    for file in files:
        with open(file, 'rb') as f:
            content = f.read()
            email = getEmail(content)
            phone = getPhone(content)
            name = file[:-5]
            data.append([name, email, phone])

    with open(outputFile, 'wb') as f:
        header = 'name\temail\tphone\r\n'
        f.write(header)
        for row in data:
            string = '\t'.join(row) + '\r\n'
            f.write(string)


def getEmail(string):
    email = ''
    emailRegEx = re.compile('\"mailto\:[0-9a-zA-Z\@\.]{1,}\"')
    m = emailRegEx.search(string)
    if m:
        email = m.group(0)[8:-1]
    return email


def getPhone(string):
    phone = ''
    phoneRegEx = re.compile('\"tel\:[\(\)\-0-9\ ]{1,}\"')
    m = phoneRegEx.search(string)
    if m:
        phone = m.group(0)[5:-1]
    return phone


if __name__ == '__main__':
    main()