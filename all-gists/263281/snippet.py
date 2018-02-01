# probably ripped off from somewhere on drupal.org
# requires the services module

import xmlrpclib
 
s = xmlrpclib.ServerProxy('http://localhost/services/xmlrpc')
 
class DrupalNode:
    def __init__(self, title, body, path, ntype='page', uid=1, username='mmatienzo'):
        self.title = title
        self.body = body
        self.path = path
        self.type = ntype
        self.uid = uid
        self.nid = 67
        self.name = username
        self.promote = True
        self.taxonomy = {'3': '3'} #how do i create new taxonomy terms???
try:
    sessid, user = s.system.connect()
    n = DrupalNode('ZA WARUDO!', 'toki wo tomare', 'saworhhhjjjdss')
    s.node.save('roadroallerdawryyy', n)
 
except xmlrpclib.Fault, err:
    print "A fault occurred"
    print "Fault code: %d" % err.faultCode
    print "Fault string: %s" % err.faultString