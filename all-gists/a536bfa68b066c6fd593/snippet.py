#!/usr/bin/env python

'''
A script to search the Mac OS X Address Book via PyObjC bridge, and 
then output the results in a format suitable for integration with
mutt.

Add the following to your `.muttrc`:

    set query_command = "~/.mutt/contacts.py '%s'"
    bind editor <Tab> complete-query
    bind editor ^T    complete
    
Then, tab-complete emails like a boss.
'''

import sys
import AddressBook as AB

# get a reference to the address book
book = AB.ABAddressBook.sharedAddressBook()

# create search parameters - prefix match on first or last name or email
firstname_search = AB.ABPersonCreateSearchElement(
    AB.kABLastNameProperty, None, None, sys.argv[1],
    AB.kABPrefixMatchCaseInsensitive
)
lastname_search = AB.ABPersonCreateSearchElement(
    AB.kABFirstNameProperty, None, None, sys.argv[1],
    AB.kABPrefixMatchCaseInsensitive
)
email_search = AB.ABPersonCreateSearchElement(
    AB.kABEmailProperty, None, None, sys.argv[1],
    AB.kABContainsSubStringCaseInsensitive
)
name_search = AB.ABSearchElement.searchElementForConjunction_children_(
    AB.kABSearchOr,
    [firstname_search, lastname_search, email_search]
)

# perform the search
matches = book.recordsMatchingSearchElement_(name_search)

# collect results
results = []
for person in matches:
    emails = person.valueForKey_('Email') or []
    company = person.valueForKey_('Organization')
    name = '%s %s' % (
        person.valueForKey_('First'),
        person.valueForKey_('Last')
    ) if person.valueForKey_('First') else company

    for i in range(len(emails)):
        results.append((
            emails.valueAtIndex_(i),
            name
        ))

# sort results
results.sort(lambda x,y: cmp(x[1], y[1]))

# output to stdout in the mutt-preferred style
print 'EMAIL\tNAME'
for result in results:
    print '%s\t%s' % result
