import sys
from rdflib import *

fpath = sys.argv[1]
prefix = sys.argv[2]

g = Graph().parse(fpath, format='n3' if fpath.endswith(('.n3', '.ttl')) else 'xml')

def name_pair(item):
    qname = item.qname()
    term = qname.split(':')[-1]
    if qname == term:
        qname = "%s:%s" % (prefix, term)
    return term, qname

for pfx, iri in g.namespaces():
    globals().setdefault(pfx.upper(), Namespace(iri))

PROTEGE = Namespace("http://protege.stanford.edu/plugins/owl/protege#")

classes, multiprops, singleprops = set(), set(), set()
ranges = {}

for r in sorted(set(g.resource(s) for s in g.subjects() if isinstance(s, URIRef))):
    if r.value(PROTEGE['abstract']):
        continue
    types = set(o.identifier for o in r.objects(RDF.type))
    range_type = r.value(RDFS.range)
    range_iri = range_type and range_type.identifier
    one = any(True for restr in r.subjects(OWL.onProperty)
            if restr.value(OWL.cardinality) == 1 or
               restr.value(OWL.maxCardinality) == 1)
    if types & {RDFS.Class, OWL.Class}:
        classes.add(r)
    elif range_iri and range_iri.startswith(XSD) or range_iri == RDFS.Literal:
        ranges.setdefault(range_type.qname(), set()).add(r)
    elif OWL.DatatypeProperty in types:
        ranges.setdefault("rdfs:Literal", set()).add(r)
    elif one or types & {RDF.Property, OWL.FunctionalProperty}:
        singleprops.add(r)
    elif OWL.ObjectProperty in types:
        multiprops.add(r)

print '  {'
for item in sorted(classes):
        print '    "%s": "%s",' % name_pair(item)
print '  }, {'
for item in sorted(multiprops):
    print '    "%s": {"@id": "%s", "@container": "@set"},' % name_pair(item)
print '  }, {'
for dtype in sorted(ranges):
    for item in sorted(ranges[dtype]):
        if dtype == "rdfs:Literal":
            print '    "%s": {"@id": "%s", "@language": null},' % (name_pair(item))
        else:
            print '    "%s": {"@id": "%s", "@type": "%s"},' % (name_pair(item) + (dtype,))
    print '  }, {'
for item in sorted(singleprops):
    print '    "%s": "%s",' % name_pair(item)
print '  }'
