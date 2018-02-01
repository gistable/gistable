# required apt-get install jython libcommons-logging-java libcommons-lang-java
import sys
sys.path.append('jackcess-2.0.4.jar') # assume the jackcess is in the same directory
sys.path.append('/usr/share/java/commons-logging-1.1.3.jar') # in case logging didn't get picked up
sys.path.append('/usr/share/java/commons-lang-2.6.jar') # in case lang didn't get picked up
from com.healthmarketscience.jackcess import *
from com.healthmarketscience.jackcess.util import ExportFilter
from com.healthmarketscience.jackcess.util import ExportUtil
from com.healthmarketscience.jackcess.util import SimpleExportFilter
import java.io
from java.io import File

dbfilename = sys.argv[1]
exportdirname = sys.argv[2]
print "input filename is",dbfilename
print "tables will be saved into directory",exportdirname
dbfile = File(dbfilename)
exportdir = File(exportdirname)
# make a database object
db = DatabaseBuilder.open(dbfile)
# make an export filter object
export_filter = SimpleExportFilter()
# use 'em to throw down all the data!
ExportUtil.exportAll(db,exportdir,'csv',True)

print "seems to work"
