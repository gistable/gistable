import os

for r,d,f in os.walk("/var/www"):
    for files in f:
        if files.endswith(".php"):
            print "You are fucked!"