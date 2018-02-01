#!/usr/bin/env python
import sys, traceback, scipy, numpy
from matplotlib import pyplot
from scipy.stats.mstats import mquantiles

def HistogramImage(data):
        print 'entered HistogramImage'
        #http://www.saltycrane.com/blog/2011/12/creating-histogram-plot-python/
        x = [int(dbyte[0]) for dbyte in data]

        binsize = 100
        totalrangeofhisto = 20000
        bins = [i * binsize for i in range(totalrangeofhisto/binsize)]

        pyplot.hist(x, bins=bins, facecolor='green', alpha=0.75)
        pyplot.xlabel('dbytes')
        pyplot.ylabel('Count')
        pyplot.suptitle(r'histogram of dbytes')
        pyplot.title(r'distribution for matt->smarsh')
        pyplot.grid(True)
        filename='histo.png'
        try:
                pyplot.savefig(filename)
                print 'saved to %s' %filename
        except:
                print 'unable to save to %s' %filename

def FindQuantile(data,findme):
        print 'entered FindQuantile'
        probset=[]
        #cheap hack to make a quick list to get quantiles for each permille value]
        for i in numpy.linspace(0,1,10000):
                probset.append(i)

        	#http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mstats.mquantiles.html
        quantile_results = mquantiles(data,prob=probset)
        #see: http://stackoverflow.com/q/17330252/
        quantiles = []
        i = 0
        for value in quantile_results:
                print str(i) +  ' permille ' + str(value)
                quantiles.append(value)
                i = i+1
        #goal is to figure out which quantile findme falls in:
        i = 0
        for quantile in quantiles:
                if (findme > quantile):
                        print str(quantile) + ' is too small for ' + str(findme)
                else:
                        print str(quantile) + ' is the quantile value for the ' + str(i) + '-' + str(i + 1) + ' per mille quantile range. ' + str(findme) + ' falls within this range.'
                        break
                i = i + 1


if __name__ == "__main__":
        import MySQLdb

        #http://www.tutorialspoint.com/python/python_database_access.htm
        #http://www.packtpub.com/article/exception-handling-mysql-python

        db = MySQLdb.connect("localhost","argus","db_password","argus" )
        cursor = db.cursor()

        sql = "SELECT dbytes FROM argus.argusTable_2013_06_24 where (saddr = '192.168.100.23' or daddr = '192.168.100.23') and daddr = '173.252.110.27' and proto = 'tcp' and dport = '443';"

        try:
                cursor.execute(sql)
                results = cursor.fetchall()
                lresults = list(results)
        except MySQLdb.Error, e:
                print "Error: %s" %e
                exit()

        db.close()

        dbytes = []
        for row in results:
                dbytes.append(int(row[0]))

        for dbyte in sorted(dbytes):
                print dbyte

        try:
                dothis = raw_input("What would you like to do? h = histogram, q = quantile ")
                if (len(dothis) == 0):
                        exit()
                elif (dothis == 'h'):
                        print 'calling HistogramImage'
                        HistogramImage(results)
                elif (dothis == 'q'):
                        andthis = raw_input('What X would you like to find the quantile for? ')
                        print 'finding Quantile for %s' %andthis
                        FindQuantile(sorted(lresults), float(andthis))
        except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print "*** print_tb:"
                traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
                print "*** print_exception:"
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                print "*** print_exc:"
                traceback.print_exc()
                print "*** format_exc, first and last line:"
                formatted_lines = traceback.format_exc().splitlines()
                print formatted_lines[0]
                print formatted_lines[-1]
                print "*** format_exception:"
                print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                print "*** extract_tb:"
                print repr(traceback.extract_tb(exc_traceback))
                print "*** format_tb:"
                print repr(traceback.format_tb(exc_traceback))
                print "*** tb_lineno:", exc_traceback.tb_lineno
                print 'exiting'
                exit()
