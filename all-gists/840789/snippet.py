#!/usr/bin/python

import json, sys, re
filename = sys.argv[1]
f = open(filename, 'r')
contents = json.load(f)

contentIndex = {}

for content in contents['content']:
    if content['type'] == 'text':
        identifier = content['identifier']
        contentIndex[identifier] = content['text']
        
headlineIndex = {}
deckIndex = {}
bylineIndex = {}

for section in contents['sections']:
    print '<h3>' + section['name'] + '</h3>'
    print '<ol>'
    for page in section['pages']:
        if page['displayOnCarousel'] == True:
            if 'webURL' in page:
                webURL = page['webURL']
                layoutIndex = {}
                for layout in page['layouts']:
                    for component in layout['components']:
                        if 'contentRefs' in component:
                            if len(component['contentRefs']) > 0:
                                contentID = component['contentRefs'][0]['contentID']
                                if contentID in contentIndex:
                                    if re.search("Head", component['title'], re.IGNORECASE):
                                        headline = re.sub('\n', ' ', contentIndex[contentID])
                                        headlineIndex[webURL] = headline
                                    if re.search("Hed", component['title'], re.IGNORECASE):
                                        headline = re.sub('\n', ' ', contentIndex[contentID])
                                        headlineIndex[webURL] = headline
                                    if re.search("Deck", component['title'], re.IGNORECASE):
                                        deck = re.sub('\n', ' ', contentIndex[contentID])
                                        deckIndex[webURL] = deck
                                    if re.search("Byline", component['title'], re.IGNORECASE):
                                        byline = re.sub('\n', ' ', contentIndex[contentID])
                                        bylineIndex[webURL] = byline

                print '<li>'
                if 'headline' in page:
                    print '<a href="' + webURL + '">' + page['headline'] + '</a>'                
                elif webURL in headlineIndex:
                    print '<a href="' + webURL + '">' + headlineIndex[webURL] + '</a>'
                else:
                    print '<a href="' + webURL + '">' + page['title'] + '</a>'

                if webURL in bylineIndex:
                    print bylineIndex[webURL]
    
                if webURL in deckIndex:
                    print '&mdash;', deckIndex[webURL]
                elif 'openingLine' in page:
                    print '&mdash;', page['openingLine']
                
                print '</li>'
    print '</ol>'