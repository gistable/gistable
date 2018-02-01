import sqlite3
import datetime
import sys


# First we connect to the sqlite db, 
# in this case it's sitting in the same
# directory and we're rocking 
# python script.py

conn = sqlite3.connect('this.db')
c = conn.cursor()
c.execute('select * from blog_post')

# Now we'll loop through the posts to 
# create txt files for each

for row in c:

    # Convert date to python datetime object
    newdate = datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')

    # Build Jekyll friendly filename
    filename = "%s-%s.md" % (datetime.datetime.strftime(newdate, '%Y-%m-%d'), row[2])
    
    # Build content of our new file
    lines = ("---\nlayout: post\ntitle: %s\n---\n\n %s" % (row[1], row[4]))
    f = open(filename, 'w')
    try:
        f.write(lines.encode('utf-8'))
    except Exception:
        # Print out every error since this is a script
        # meant for nerds
        e = sys.exc_info()[1]
        print "Error: %s" % e
    f.close()