from plistlib import readPlist
from cgi import escape
from lxml.etree import SubElement as sub
import lxml.etree

# Load in apple mail rules file
rules_file = '~/Library/Mail/V2/MailData/SyncedRules.plist'
rules = readPlist(rules_file)

# Create gmail filters xml header
APPS_NAMESPACE = 'http://schemas.google.com/apps/2006'
NSMAP = {None: 'http://www.w3.org/2005/Atom', 'apps': APPS_NAMESPACE}
feed = lxml.etree.Element('feed', nsmap=NSMAP)
title = sub(feed, 'title').text = 'Mail Filters'

author = sub(feed, 'author')
sub(author, 'name').text = 'Adam Walz'
sub(author, 'email').text = 'adam@adamwalz.net'

# Parse apple mail rules
prop = '{' + APPS_NAMESPACE + "}property"
for rule in rules:
    if rule['Criteria'][0]['Header'] == 'AnyMessage':
        continue

    # All mail rules have the following sub elements
    entry = sub(feed, 'entry')
    sub(entry, 'category', attrib={'term': 'filter'})
    sub(entry, 'title').text = 'Mail Filter'
    sub(entry, 'content')

    logic = ' OR ' if rule['AllCriteriaMustBeSatisfied'] == 'NO' else ''

    # Create rule string
    newcriteria = ''
    for criteria in rule['Criteria']:
        if newcriteria:
            newcriteria = newcriteria + logic

        qual = '+"' if criteria.get('Qualifier') == 'IsEqualTo' else '('
        negation = ' -' if criteria.get('Qualifier') == 'DoesNotContain' \
            else ''
        exp = qual + criteria['Expression']

        header = criteria['Header']

        if header == 'From':
            newcriteria = newcriteria + negation + 'from:' + exp
        elif header == 'To' or header == 'AnyRecipient':
            newcriteria = newcriteria + negation + 'deliveredto:' + exp
        elif header == 'Subject':
            newcriteria = newcriteria + negation + 'subject:' + exp
        elif header == 'Body':
            newcriteria = newcriteria + negation + exp

        if criteria.get('Qualifier') == 'IsEqualTo':
            newcriteria = newcriteria + '"'
        else:
            newcriteria = newcriteria + ')'

    newcriteria = escape(newcriteria)

    # Create label
    label = []
    for part in rule.get('CopyToMailbox', '').split('/'):
        if part.endswith('.mbox'):
            label.append(part.rstrip('.mbox').lower())

    # sub elements unique to rule
    sub(entry, prop, attrib={'name': 'hasTheWord', 'value': newcriteria})
    sub(entry, prop, attrib={'name': 'label', 'value': '/'.join(label)})

# Print gmail filters
# print(lxml.etree.tostring(feed,
#       xml_declaration=True,
#       encoding="utf-8",
#       pretty_print=True))
print(lxml.etree.tounicode(feed))
