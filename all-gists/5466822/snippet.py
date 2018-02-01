#!/usr/bin/python
#increment the SOA by 1 - I know we could do better
import MySQLdb, sys
pdns_backend_config_file="/etc/powerdns/pdns.d/pdns.local.gmysql" # this is the file where mysql access is defined for pdns
a=open(pdns_backend_config_file)
domain=sys.argv[1] # stupid assumption



def getConfig(confFile):
    """Parses config from pdns format and store in dict"""
    myConf={}
    for config in a.readlines():
        if "=" in config:
            confsplit=config.split("=")
            myConf[confsplit[0]]=confsplit[1].strip()
    connDict={
        'host':myConf["gmysql-host"],
        'user':myConf["gmysql-user"],
        'passwd':myConf["gmysql-password"],
        'db':myConf["gmysql-dbname"]
        }
    return connDict
        
def connMySQL(connDict):
    """Create a connection to MySQL"""
    conn=MySQLdb.connect(
        host=connDict["host"],
        user=connDict["user"],
        passwd=connDict["passwd"],
        db=connDict["db"]
        )
    return conn

def getDomainID(conn,domain):
    """Get the ID of the domain to be updated from the Database"""
    c=conn.cursor()
    r=c.execute("select * from domains where domains.name=%s" , domain)
    try: 
        domID=c.fetchone()[0] 
    except:
        exit("No such domain")
    return domID


def incSOARecord(conn,domID):
    c=conn.cursor()
    print "Updating:",domID
    r=c.execute("select id,content from records where domain_id=%s and type='SOA' " , domID)
    id,soa=c.fetchone()
    soasplit=soa.split(" ")
    soasplit[2]="%s" % (int(soasplit[2])+1)
    newsoa=" ".join(soasplit)
    r=c.execute("update records set content=%s where id=%s" , (newsoa,id))
    conn.commit()


print "Trying to increment SOA on %s." % domain
connDict=getConfig(pdns_backend_config_file)
conn=connMySQL(connDict)
domainID=getDomainID(conn,domain)
incSOARecord(conn,domainID)
