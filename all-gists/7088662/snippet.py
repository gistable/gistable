# Note: Requires mysqldb; install using:
# pip install MySQL-python
from MySQLdb.constants import FIELD_TYPE
import _mysql

db = None

def fetch_gene_coordinates(gene_name,build):
	global db # db is global to prevent reconnecting.
	if db is None:
		print 'connect'
		conv= { FIELD_TYPE.LONG: int }
		db = _mysql.connect(host='genome-mysql.cse.ucsc.edu',user='genome',passwd='',db=build,conv=conv)
	db.query("""SELECT * FROM kgXref INNER JOIN knownGene ON kgXref.kgID=knownGene.name WHERE kgXref.geneSymbol = '%s'""" % gene_name)

	r = db.use_result().fetch_row(how=1,maxrows=0)
	print r
	if len(r)>1:
		pass
	else:
		return r[0]['txStart'], r[0]['txEnd'], r[0]['chrom'],r[0]['strand']


print fetch_gene_coordinates('klf1','mm9')





