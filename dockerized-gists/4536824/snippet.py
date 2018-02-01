import urllib2, json, pprint, re, datetime
import mwparserfromhell

def _parseDate(wikiDate):
  ''' Parse a mediawiki date template -- assumes years, month, day
  Input:
    a mwparser object containing just the date to be parsed
  Returns:
    datetime.date object of the date
  '''
  template = mwparserfromhell.parse("%s"%wikiDate.value)
  d = map(template.filter_templates()[0].get, [1,2,3])
  d = [int('%s'%x.value) for x in d]
  return datetime.date(*d)


def _parseInfobox(page):
  '''Parse out the nice mediawiki markdown to get birth and death
  Input:
    mediawiki unicode page string
  Returns:
    a dictionary with name(string), birth_date:DateTime, death_date:DateTime
  '''
  try:
    code = mwparserfromhell.parse(page)
    for template in code.filter_templates():
      if 'Infobox' in template.name:
        # Found the right template -- attempting to extract data
        output = {}
        output['name'] = "%s"%template.get('name').value
        # birth = _parseDate(template.get('birth_date'))
        # death = _parseDate(template.get('death_date'))
        # Do it a bit safer by catching missing values
        for date in ['birth_date', 'death_date']:
          try:
            item = _parseDate(template.get(date))
          except ValueError as e:
            item = None
          output[date] = item

        # ok we are done here
        return output
        
    raise ValueError('Missing InfoBox')

  except Exception as e:
    print "Failed to parse find infobox or something else"
    raise e


def wikiAge(wikiTitle, function=None):
  ''' Parse a wikipedia url to run a function on the data
  Input:
    wikiTitle : Title of a wiki page for an individual with born and died date
    function : a python function which operates on a mediawikipage
  Output:
    Person Dictionary with ['name', 'birth_date', 'death_date'

  Example:
    person = wikiDate('Albert_Einstein', function=_parseInfobox)
    assert person['name'] == 'Albert Einstein'
    assert person['birth_date'] == datetime.date(1879, 03, 14) # '14 March 1879'
    assert person['death_date'] == datetime.date(1955, 04, 18) # '18 April 1955'
  '''
  URLTEMPLATE = 'http://en.wikipedia.org/w/api.php?format=json&action=query&titles=%s&prop=revisions&rvprop=content'
  
  # Attempt to read page otherwise error out on all errors
  try:
    pageJson = urllib2.urlopen(URLTEMPLATE%(wikiTitle)).readlines()[0]
  except Exception as e:
    print "Failed to Read page: %s"%(URLTEMPLATE%(wikiTitle))
    raise e

  # Now that we have some json Data
  try:
    page = json.loads(pageJson)
    # The data is three dictionaries deep:
    # Ignoring the extra data
    page = page['query']['pages']
    pageid = page.keys()[0]
    page = page[pageid]['revisions'][0]['*'] 
    # Page should now contain the mediawiki unicode markup text
    # runs function to try to grab what you want out of it
    # print page
    return function(page)

  except Exception as e:
    print 'Failed to process Page -- Probably means that the wiki page was missing something important'
    raise e

if __name__ == '__main__':
  person = wikiAge('Albert_Einstein', function=_parseInfobox)
  for key in person:
    print 'Key:%s  Value: %s'%(key,person[key])

  person = wikiAge('Galileo_Galilei', function=_parseInfobox)
  for key in person:
    print 'Key:%s  Value: %s'%(key,person[key])

  person = wikiAge('Mark_Zuckerberg', function=_parseInfobox)
  for key in person:
    print 'Key:%s  Value: %s'%(key,person[key])
