"""
Use the Vivo harverster with Python and Jnius.

You need to set the Java classpath before running this. 
e.g.
    export CLASSPATH=".:/work/javalib/*"

The path you specify needs to contain the Vivo Harvester jar.  

https://github.com/vivo-project/VIVO-Harvester

"""

from jnius import autoclass


SDBJenaConnect = autoclass('org.vivoweb.harvester.util.repo.SDBJenaConnect')
SimpleSelector = autoclass('com.hp.hpl.jena.rdf.model.SimpleSelector')

class VivoConn(object):
    """
    A connection to Vivo SDB using the Vivo harvester.

    Pass in a dictionary with the connection details.

    {
     'db_url': 'vivo.school.edu/vivodb',
     'namespace': 'http://vivo.school.edu/individual/',
     'user': 'admin'
     'password': 'pass',
    }

    """

    def __init__(self, conf):
        db_url = conf.get('db_url')
        self.conn = SDBJenaConnect(
            'jdbc:mysql://%s' % db_url,
            conf.get('user'),
            conf.get('password'),
            conf.get('db_type', 'MySQL'),
            #class
            conf.get('db_driver', 'com.mysql.jdbc.Driver'),
            #layout
            conf.get('layout', 'layout2'),
            #modelname
            conf.get('layout', 'http://vitro.mannlib.cornell.edu/default/vitro-kb-2')
        )
        self.namespace = conf.get('namespace')

    def close(self):
        self.conn.close()

    def get_next_uri(self, max=9999999):
        """
        Get a random identifer to use as a resource uri.

        Interpretation of getNextURI here:
        http://svn.code.sf.net/p/vivo/vitro/code/branches/dev-sdb/webapp/src/edu/cornell/mannlib/vitro/webapp/utils/jena/JenaIngestUtils.java
        """
        import random
        model = self.conn.getJenaModel()
        next_uri = None
        if self.namespace is None:
            raise Exception('Namespace is None; set it.')
        while True:
            next_uri = self.namespace + 'n' + str(random.randint(1, max))
            resource = model.createResource(next_uri)
            #Check if this uri is the subject of any statements.
            sub_selector = SimpleSelector(resource, None, None)
            sub_iter = model.listStatements(sub_selector)
            if sub_iter.hasNext():
                sub_iter.close()
                continue
            else:
                #Check if this uri is the object of any statements.
                obj_selector = SimpleSelector(None, None, resource)
                obj_iter = model.listStatements(obj_selector)
                if obj_iter.hasNext():
                    obj_iter.close()
                    continue
                else:
                    break
        return next_uri


    def get_or_next(self, vtype, label):
        """
        Pass in a vivo type and a label to fetch the matching
        resource or return a next random identifier for creating
        resource.
        """
        query = """
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        select ?uri
        where {
               ?uri a %(vtype)s.
               ?uri rdfs:label "%(label)s".
        }
        LIMIT 1
        """ % {'vtype': vtype, 'label': label}
        result_iter = self.conn.executeSelectQuery(query)
        while True:
            if result_iter.hasNext():
                next_result = result_iter.next()
                uri = next_result.get('?uri').toString()
                return (uri, False)
            else:
                break
        #If we are here, we need to generate a new uri.
        next_uri = self.get_next_uri()
        return (next_uri, True)


    