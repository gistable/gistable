"""Script to extract voter info from voter rolls.

This script expects the extracted text file from the voter-list pdf.

It can be done using:

    $ pdftotext -layout AC1580002.pdf

"""
import sys
import re
import json

re_voterid = re.compile("([#ESQR]?) *([0-9]+) +([A-Z]{3}[0-9]{7})")
def read_strips(f):
    """Reads strips of voterid.

    Each strip contains a maximum of 3 voterids listed in 3 columns.
    """
    re_photo = re.compile("(Photo| Not| Available)")

    strip = None
    for line in f:
        line = re_photo.sub("", line)

        #print repr(line), re_voterid.search(line)
        if re_voterid.search(line):
            if strip:
                yield strip[:8]
            strip = []
            strip.append(line)
        elif strip is not None:
            strip.append(line)

    if strip:
        yield strip[:8]

def read_pages(f, skip_headers=True):
    text = f.read()
    for page in text.split('\x0c'):
        if page.strip().startswith("Electoral Roll 2014 of"):
            lines = page.strip().splitlines()
            if skip_headers:
                lines = strip_headers(lines)
            yield lines

def select_window(lines, start_col, end_col):
    return [line[start_col:end_col] for line in lines]

def read_columns(pages):
    for page in pages:
        w0 = select_window(page, 0, 45)
        w1 = select_window(page, 45, 90)
        w2 = select_window(page, 90, 1000)
        lines = w0 + w1 + w2
        lines = (line.strip() for line in lines if line.strip())
        for line in lines:
            yield line
        
def strip_headers(lines):
    patterns = ["Age as on", "Delete Reason:", "Electoral Roll", "Section No"]
    for line in lines:
        if not any(line.strip().startswith(p) for p in patterns):
            yield line

def group_voters(lines):
    re_begin = re.compile('^(\d+) +([A-Z][A-Z][A-Z]\d+)')
    re_age = re.compile("Age: (\d+)")
    re_sex = re.compile("Sex: ([a-zA-Z]*)")
    re_relation = re.compile("(?:Father|Mother|Husband)'s (.*)")
    voter = None
    genders  = dict(male="M", female="F")

    for line in lines:
        m = re_begin.match(line)
        if m:
            if voter:
                yield voter
            voter = {}
            voter['serial'] = m.group(1)
            voter['voterid'] = m.group(2)
            for k in ["name", "rel_name", "age", "sex"]:
                voter[k] = "-"

        if not voter:
            continue

        if line.startswith("Name : "):
            voter['name'] = line[len('Name :'):].strip()

        if "Sex:" in line:
            m = re_sex.search(line)
            sex = m and m.group(1)
            if sex:
                voter['sex'] = genders.get(sex.lower().strip(), "-")

        if "Age:" in line:
            m = re_age.search(line)
            voter['age'] = m and m.group(1)

        m = re_relation.match(line)
        if m:
            voter['rel_name'] = m.group(1).strip()

def find_part(filename):
    re_part = re.compile("Part No. (\d+)")
    text = open(filename).read(1000)
    m = re_part.search(text)
    return m.group(1)

def sanitize_voter(voter):
    def sanitize(value):
        return value and value.decode('utf-8', 'ignore')
    return dict((k, sanitize(v)) for k, v in voter.items())

def parse_file(filename):
    part = find_part(filename)
    f = open(filename)
    pages = read_pages(f)
    pages = list(pages)

    page3 = list(pages[3])

    for line in page3:
        print repr(line)

    #return

    lines = read_columns([page3])

    lines = list(lines)
    for x in lines[:100]:
        print x

    return

    for voter in group_voters(lines):
        voter['part'] = part
        voter = sanitize_voter(voter)
        print "xx", voter
        print json.dumps(voter)

def is_empty(voter):
    return not any(line.strip() for line in voter)



def read_voters(f):
    for strip in read_strips(f):
        """
        print "-" * 100
        for line in strip:
            print line.strip()
        """
        v0 = select_window(strip, 0, 45)
        v1 = select_window(strip, 45, 90)
        v2 = select_window(strip, 90, 1000)

        for v in [v0, v1, v2]:
            if not is_empty(v):
                yield v

def parse_voter(lines):
    # just like the re_voterid above, but voterid is optional.
    # some voter entries don't have voterid specified
    re_voterid = re.compile("([#ESQR]?) *([0-9]+) +([A-Z]{3}[0-9]{7})?")

    re_age = re.compile("Age: (\d+)")
    re_sex = re.compile("Sex: ([a-zA-Z]*)")
    re_relation = re.compile("(?:Father|Mother|Husband)'s (.*)")
    voter = None
    genders  = dict(male="M", female="F")

    m = re_voterid.match(lines[0].strip() + " ")
    if not m:
        return None
    flag, serial, voterid = m.groups()
    if voterid is None: # rare cases
        voterid = "-"
    voter = dict(voterid=voterid, serial=serial, flag=flag)

    for k in ["name", "rel_name", "age", "sex"]:
        voter[k] = "-"

    for line in lines[1:]:
        line = line.strip()
        if line.startswith("Name : "):
            voter['name'] = line[len('Name :'):].strip()

        if "Sex:" in line:
            m = re_sex.search(line)
            sex = m and m.group(1)
            if sex:
                voter['sex'] = genders.get(sex.lower().strip(), "-")

        if "Age:" in line:
            m = re_age.search(line)
            voter['age'] = m and m.group(1)

        m = re_relation.match(line)
        if m:
            voter['rel_name'] = m.group(1).strip()
    return voter

def main():
    filename = sys.argv[1]
    part = find_part(filename)
    f = open(filename)
    voters = [parse_voter(v) for v in read_voters(f)]
    voters = [v for v in voters if v]

    """
    for v in voters:
        v['part'] = part
        print json.dumps(v)

    return
    """

    # skip duplicates by adding them to a dict
    # modifications, deletions result in duplicate entries
    voterdict = dict((v['serial'], v) for v in voters)

    # skip deletes
    voters = [v for v in voterdict.values() if v['flag'] not in ['E', 'S', 'Q', 'R']]

    voters = sorted(voters, key=lambda v: int(v['serial']))
    for v in voters:
        v['part'] = part
        v = sanitize_voter(v)
        print json.dumps(v)

if __name__ == "__main__":
    main()


