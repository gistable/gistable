import csv
import ldif
import sys


def flatten(d, bar='|'):
    """
    Take a regular dictionary, and flatten the value if it's a list.
    """
    diff = {}
    for k, v in d.items():
        if not isinstance(v, basestring):
            diff[k] = bar.join(v)
    d.update(diff)
    return d


class MyParser(ldif.LDIFParser):

    def __init__(self, *args, **kwargs):
        ldif.LDIFParser.__init__(self, *args, **kwargs)
        self.attributes = set()
        self.records = []

    def handle(self, dn, entry):
        self.attributes.update(entry.keys())
        self.records.append(entry)

    def csv(self, fp=sys.stdout):
        writer = csv.DictWriter(fp, fieldnames=self.attributes)
        try:
            writer.writeheader()
        except AttributeError:
            fields = sorted(self.attributes)
            writer.writerow(dict(zip(fields, fields)))
        for record in self.records:
            writer.writerow(flatten(record))


p = MyParser(sys.stdin)
p.parse()
p.csv()
