import requests, re, json, types, traceback

class HypothesisAnnotation:

    def __init__(self, row):
        """Encapsulate relevant parts of one row of a Hypothesis API search."""

        self.tags = []
        if row.has_key('tags') and row['tags'] is not None:
            self.tags = row['tags']
            if isinstance(self.tags, types.ListType):
                self.tags = [t.strip() for t in self.tags]

        self.text = ''
        if row.has_key('text'):
            self.text = row['text']

        self.target = []
        if row.has_key('target'):
            self.target = row['target']

        self.start = self.end = self.prefix = self.exact = self.suffix = None
        try:
            if isinstance(self.target,list) and len(self.target) and self.target[0].has_key('selector'):
                selectors = self.target[0]['selector']
                for selector in selectors:
                    if selector.has_key('type') and selector['type'] == 'TextQuoteSelector':
                        try:
                            self.prefix = selector['prefix']
                            self.exact = selector['exact']
                            self.suffix = selector['suffix']
                        except:
                            traceback.print_exc()
                    if selector.has_key('type') and selector['type'] == 'TextPositionSelector' and selector.has_key('start'):
                        self.start = selector['start']
                        self.end = selector['end']
                    if selector.has_key('type') and selector['type'] == 'FragmentSelector' and selector.has_key('value'):
                        self.fragment_selector = selector['value']
        except:
            print traceback.format_exc()

canonical_url = raw_input("Canonical URL?")
alternate_url = raw_input("Annotated URL?")
query_url = 'https://hypothes.is/api/search?uri=%s' % alternate_url
text = requests.get(query_url).text.decode('utf-8')
rows = json.loads(text)['rows']
h_annotations = [HypothesisAnnotation(row) for row in rows]

def filter_tags_by_prefix(tags, tag_prefix):
    return [tag for tag in tags if tag.lower().startswith(tag_prefix.lower())]

def has_tag_starting_with(h_annotation, tag_prefix):
    filtered = filter_tags_by_prefix(h_annotation.tags, tag_prefix)
    return len(filtered) > 0

def get_tag_starting_with(h_annotation, tag_prefix):
    filtered = filter_tags_by_prefix(h_annotation.tags, tag_prefix)
    if len(filtered) > 0:
        return filtered[0]
    else:
        return None

def select_annotations_with_tag_prefix(rows, tag_prefix):
    return [h_annotation for h_annotation in h_annotations if has_tag_starting_with(h_annotation, tag_prefix)]

def make_interpretation_element(h_annotations, tag_prefix):
    list = []
    h_annotations = select_annotations_with_tag_prefix(rows, tag_prefix)
    for h_annotation in h_annotations:
        tag = get_tag_starting_with(h_annotation, tag_prefix)
        subtag = tag.split(':')[1]
        list.append(subtag + ': ' + h_annotation.exact)
    return list

def make_abstract(h_annotations):
    html = """
**Title:** %s

**Subject:** %s

**Key Themes:** %s

**Key Literature:** %s

**The Interesting Bits:**

%s""" % (
        select_annotations_with_tag_prefix(h_annotations, 'Title')[0].exact,
        ', '.join(make_interpretation_element(h_annotations, 'Subject')),
        ', '.join(make_interpretation_element(h_annotations, 'Keytheme')),
        ', '.join(make_interpretation_element(h_annotations, 'Keylit')),
        '<ul><li>' + '</li><li>'.join(make_interpretation_element(h_annotations, 'Item')) + '</li></ul>' )
    return html

def subfindings_from_h_annotation(h_annotation):
    body = re.sub('\n*<.+>\n*', '', h_annotation.text)
    rows = []
    chunks = body.split('\n\n')
    for chunk in chunks:
        fields = chunk.split('\n')
        fields = [re.sub('\w+:\s+','',field) for field in fields]
        rows.append('<tr><td>' + '</td><td>'.join(fields) + '</td></tr>')
    return rows

def make_table(h_annotations):
    rows = []
    raw_findings = select_annotations_with_tag_prefix(h_annotations, 'Item')
    for raw_finding in raw_findings:
        rows += subfindings_from_h_annotation(raw_finding)
    html = '<table>'
    headers = ['Observation','Resonances','Crossref','Problems'] #these are headings you'd use in your actual annotation. change as appropriate
    html += '<tr><th>' + '</th><th>'.join(headers) + '</th></tr>'
    html += '\n'.join(rows)
    html += '</table>'
    return html

html = """
<style>

table, td, th { border-collapse: collapse; border: 1px solid black }
td { padding: 6px }
th { padding: 6px; background-color: lightgrey}
</style>

## Reading report
for [%s](%s)

### Summary
%s

### Tabular Representation
%s

 """ % ( canonical_url, canonical_url, make_abstract(h_annotations), make_table(h_annotations) )

savefileas = raw_input("save the report as?")
f = open(savefileas+'.md','w')
f.write(html.encode('utf-8'))
f.close()
