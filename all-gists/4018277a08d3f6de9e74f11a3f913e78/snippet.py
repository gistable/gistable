import csv
import cStringIO
import codecs
import glob
import json
import requests


def fetch_jsons():
    url = ('https://summerofcode.withgoogle.com/api/program/current/project/'
           '?page=%d'
           '&page_size=10')

    for page in range(1, 126):

        obj = requests.get(url % page).json()

        # Finished
        if 'results' not in obj:
            print("Ending")
            break

        # Save each project into a separate json
        # (i like having all data locally)
        for result in obj['results']:
            fpath = 'projects/%s.json' % str(result['id'])
            print(fpath)
            with open(fpath, 'w') as out:
                json.dump(result, out, indent=4, sort_keys=True)


# Copied from SO!
# Why do I have to do this everytime :/
class UnicodeCSVWriter:

    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        '''writerow(unicode) -> None
        This function takes a Unicode string and encodes it to the output.
        '''
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def generate_csv():
    outcsv = UnicodeCSVWriter(open("projects.csv", "w"), quoting=csv.QUOTE_ALL)

    for file in glob.glob('projects/*.json'):
        with open(file, 'r') as inp:
            project = json.load(inp)

        outcsv.writerow((
            project['title'],
            project['student']['display_name'],
            project['organization']['name'],
            ", ".join(project['assignee_display_names']),
        ))

if __name__ == '__main__':
    # fetch_jsons()
    generate_csv()
