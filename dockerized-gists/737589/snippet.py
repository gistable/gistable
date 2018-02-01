#!/usr/bin/env python
"""Get title/author for ISBNs in a Google Docs spreadsheet."""

from getpass import getpass
import os
import os.path
import sys

from gdata.spreadsheet import service, SpreadsheetsList
from gdata.books import service as bservice


def usage(msg=None):
    """Tell the user how to use this program."""

    if msg:
        sys.stderr.write(msg + '\n\n')
    sys.stderr.write('''\
usage: %s username spreadsheetname

You will be asked for the password, or you can place it in the environment
variable IPASS.  If there is no "@" in the username, "@gmail.com" will be
appended to it.

The spreadsheet must have at least three columns: ISBN, Title, Author
(capitalization does not matter).  I will fetch ISBNs from the "isbn" column
and insert titles and authors in their respective columns.

If there is a column named "status", it will be filled in with any error
messages that occur while searching for the ISBN.

I will ignore rows where the title column is already filled in.

*** I will ask before modifying the spreadsheet. ***

''' % os.path.basename(sys.argv[0]))
    sys.exit(1)


def login(username):
    """Logon to AOL today!"""

    if username.find('@') == -1:
        username += '@gmail.com'
    print('Username: %s' % username)
    password = os.environ.get('IPASS')
    if not password:
        password = getpass('Password: ')
    if not password or len(password) < 4:
        usage('invalid password')

    sclient = service.SpreadsheetsService()
    bclient = bservice.BookService()
    bclient.email = sclient.email = username
    bclient.password = sclient.password = password
    bclient.source = sclient.source = 'fn-booklist'
    sclient.ProgrammaticLogin()
    bclient.ProgrammaticLogin()
    print('Logged in.')

    return (sclient, bclient)


def findsheet(sclient, sheet):
    """Find the spreadsheet."""

    feed = sclient.GetSpreadsheetsFeed()
    found = None
    for doc in feed.entry:
        if doc.title.text == sheet:
            found = doc
            break
        elif doc.title.text.lower() == sheet.lower():
            found = doc
            break

    if not found:
        usage('%s not found' % sheet)

    skey = found.id.text.rsplit('/', 1)[1]
    wfeed = sclient.GetWorksheetsFeed(skey)
    wkey = wfeed.entry[0].id.text.rsplit('/', 1)[1]

    return (skey, wkey)


def findcolumn(entry, colname, required=True):
    """Check if a column exists."""

    col = None
    for heading in entry.custom.keys():
        if heading.lower().find(colname.lower()) != -1:
            col = heading
            break

    if not col and required:
        usage('%s column not found in spreadsheet' % colname)

    return col


def displayfound(bookdata):
    """Show the user what we've found."""

    for isbn, data in bookdata.items():
        print('    ISBN: %13s\n    Title: %s\n    Author(s): %s' %
              (isbn, data[0], data[1]))

        
def doit(sclient, skey, wkey, bclient):
    """Do the work.

    #1 identify columns.
    #2 get a list of all ISBNs where related title cell is empty.
    #3 fetch title, author data.
    #4 ask user, then insert.
    """

    lfeed = sclient.GetListFeed(skey, wkey)

    # check for the required columns headings,
    # and note down their exact names.
    isbncol = findcolumn(lfeed.entry[0], 'ISBN')
    titlecol = findcolumn(lfeed.entry[0], 'Title')
    authorcol = findcolumn(lfeed.entry[0], 'Author')
    statuscol = findcolumn(lfeed.entry[0], 'Status', required=False)

    # tuples of (row, isbn)
    # index points to the row in lfeed.entry array
    workrows = []
    skipcount = 0

    for idx in range(len(lfeed.entry)):
        row = lfeed.entry[idx]
        if not row.custom[isbncol].text:
            skipcount += 1
        elif row.custom[titlecol].text:
            skipcount += 1
        else:
            isbn = row.custom[isbncol].text.replace('-', '').upper()
            if isbn:
                workrows.append((idx, isbn))
            else:
                skipcount += 1

    print('ISBNs found: %d, skipped: %d' % (len(workrows), skipcount))

    # key: isbn, value: tuple of (title, author)
    bookdata = {}
    # search errors.  key: isbn, value: message 
    status = {}

    # search
    for row in workrows:
        try:
            rfeed = bclient.search(row[1])
        except Exception, exc:
            status[row[1]] = str(exc)
            continue

        if rfeed.entry:
            # assume the first entry is the one we want
            # TODO: ask the user
            book = rfeed.entry[0].to_dict()
            bookdata[row[1]] = (book.get('title', ''),
                                ', '.join(book.get('authors', [])))
        else:
            print('No data found for %s.' % row[1])
            status[row[1]] = 'no match'

    displayfound(bookdata)

    if not len(bookdata):
        print('Nothing to update.')
        sys.exit(0)

    yorn = raw_input('\nShall I update the spreadsheet? [y/N] ')
    if not yorn or yorn[0] not in ('y', 'Y'):
        print('Bye!')
        sys.exit(0)

    for (idx, isbn) in workrows:
        row = lfeed.entry[idx]
        if isbn in bookdata:
            udict = {}
            for key, value in row.custom.items():
                udict[key] = value.text
            udict[titlecol] = bookdata[isbn][0]
            udict[authorcol] = bookdata[isbn][1]
            # udict = { titlecol : bookdata[isbn][0],
            #           authorcol : bookdata[isbn][1] }
            newrow = sclient.UpdateRow(row, udict)
            if isinstance(newrow, SpreadsheetsList):
                print('Updated entry for %13s' % isbn)
        elif isbn in status and statuscol:
            udict = {}
            for key, value in row.custom.items():
                udict[key] = value.text
            udict[statuscol] = status[isbn]
            newrow = sclient.UpdateRow(row, udict)
            if isinstance(newrow, SpreadsheetsList):
                print('Updated status for %13s' % isbn)


def main(args):
    """Main branching logic."""

    if len(args) != 2:
        usage('not enough arguments')

    (sclient, bclient) = login(args[0])

    name = args[1]
    print('Searching for a spreadsheet named "%s"...' % name)

    (skey, wkey) = findsheet(sclient, name)
    print('Spreadsheet found, worksheet found.')

    doit(sclient, skey, wkey, bclient)
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])

# eof
