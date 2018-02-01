# Where to get the data:
# https://catalog.data.gov/dataset/crimes-2001-to-present-398a4
# THIS IS A BIG FILE - 1.5 gig
# prints the Headers and the First Line
# USAGE EXAMPLE: python HeadFirst.py Crimes_-_2001_to_present.csv  
import sys
filename = sys.argv[1]
def headFirst(filename):
    N=1000
    f=open(filename)
    count=0
    starT = 0
    enD = 1
    for i in range(N):
        count=count+1
        line=f.next().strip()
        if count > starT:
            print "LineNumber :",count,"\n",line,"\n"
            if count >enD:
                sys.exit()

    f.close()
    
if __name__ == "__main__":
    headFirst(filename)