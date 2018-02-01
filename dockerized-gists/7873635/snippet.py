from rdflib import *


SDO = Namespace("http://schema.org/")

datatype_coerce_map = {
    #SDO.Number: XSD.double,
    SDO.Date: 'xsd:date',
    SDO.DateTime: "xsd:dateTime",
}

def make_context(graph, use_vocab=False, dt_coercion=False, object_coercion=False):
    ctx = {'xsd': unicode(XSD)}
    if use_vocab:
        ctx['@vocab'] = SDO
    else:
        for cls in graph[:RDF.type:RDFS.Class]:
            term_key = graph.value(cls, RDFS.label)
            ctx[term_key] = unicode(cls)

    for prop in graph[:RDF.type:RDF.Property]:
        term_key = graph.value(prop, RDFS.label)
        ranges = list(graph.objects(prop, SDO.rangeIncludes))
        coercion = None
        if len(ranges) == 1:
            if ranges[0] == SDO.URL:
                coercion = "@id"
            elif dt_coercion:
                coercion = datatype_coerce_map.get(ranges[0])
        elif object_coercion and not any(SDO.DataType in
                graph.objects(rng, RDFS.subClassOf*'*') for rng in ranges):
            coercion = "@id"
        if coercion:
            dfn = ctx[term_key] = {"@type": coercion}
            if not use_vocab:
                dfn["@id"] = unicode(prop)
        elif not use_vocab:
            ctx[term_key] = unicode(prop)

    return {"@context": ctx}


if __name__ == '__main__':
    from sys import argv
    import json
    from rdflib.util import guess_format

    args = argv[1:]
    source = args.pop(0)
    use_vocab = '-V' not in args
    dt_coercion = '-d' in args
    object_coercion = '-o' in args

    graph = Graph().parse(source, format=guess_format(source))
    context = make_context(graph, use_vocab, dt_coercion, object_coercion)

    s = json.dumps(context, sort_keys=True, indent=2, separators=(',', ': '),
            ensure_ascii=False).encode('utf-8')

    import re
    print re.sub(r'{\s+(\S+: "[^"]+")\s+}', r'{\1}', s)
