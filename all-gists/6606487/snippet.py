'''
Created on Sep 7, 2013

@author: anuvrat
'''
import pickle
from datetime import datetime
import urllib.request
from bs4 import BeautifulSoup
import re
import string
import json
import codecs

def loadState():
    try:
        state_file = open( "itunes_store_state_dump.pba", "rb" )
        apps_discovered = pickle.load( state_file )
        apps_pending = pickle.load( state_file )
        state_file.close()
        print( "Pending = ", len( apps_pending ), " Discovered = ", len( apps_discovered ) )
        return apps_discovered, apps_pending
    except IOError:
        print( "A fresh start ..." )
        return [], []

character_encoding = 'utf-8'
apps_discovered, apps_pending = loadState()
count_offset = len( apps_discovered )
apps_categories = {}

start_time = datetime.now()

def getPageAsSoup( url ):
    try:
        response = urllib.request.urlopen( url )
    except urllib.error.HTTPError as e:
        print( "HTTPError with: ", url, e )
        return None
    the_page = response.read()
    soup = BeautifulSoup( the_page )

    return soup

def reportProgress():
    current_time = datetime.now()
    elapsed = current_time - start_time
    v = ( ( len( apps_discovered ) - count_offset ) / elapsed.seconds ) * 60
    t = len( apps_pending ) / v if v > 0 else 0
    print( "Pending = ", len( apps_pending ), " Discovered = ", len( apps_discovered ), " Velocity = ", str( v ), " parsed per min and Time remaining in min = ", str( t ) )
    print( json.dumps( apps_categories ) )

def saveState():
    state_file = open( "itunes_store_state_dump.pba", "wb" )
    pickle.dump( apps_discovered, state_file )
    pickle.dump( apps_pending, state_file )
    state_file.close()
    reportProgress()

def getApps( categoryUrl ):
    previous_apps = []
    start_idx = 1
    while( True ):
        url = categoryUrl + "&page=" + str( start_idx )
        print( url )
        categoryPage = getPageAsSoup( url )
        allAppLinks = [aDiv.get( 'href' ) for aDiv in categoryPage.findAll( 'a', href = re.compile( '^https://itunes.apple.com/us/app' ) )]
        if allAppLinks == previous_apps: break
        apps_pending.extend( [appLink for appLink in allAppLinks if appLink not in apps_pending] )
        previous_apps = allAppLinks
        start_idx += 1
    saveState()

def getAppDetails( appUrl ):
    if appUrl in apps_discovered: return None
    soup = getPageAsSoup( appUrl )
    if not soup: return None

    pTitleDiv = soup.find( 'p', {'class' : 'title'} )
    if pTitleDiv and pTitleDiv.getText() == 'One Moment Please.': return None

    appDetails = {}
    appDetails['app_url'] = appUrl

    titleDiv = soup.find( 'div', {'id' : 'title'} )
    appDetails['title'] = titleDiv.find( 'h1' ).getText()
    appDetails['developer'] = titleDiv.find( 'h2' ).getText()

    detailsDiv = soup.find( 'div', {'id' : 'left-stack'} )
    if not detailsDiv: return None

    priceDiv = detailsDiv.find( 'div', {'class' : 'price'} )
    if priceDiv: appDetails['price'] = priceDiv.getText()

    categoryDiv = detailsDiv.find( 'li', {'class' : 'genre'} )
    if categoryDiv: appDetails['category'] = categoryDiv.find( 'a' ).getText()

    releaseDateDiv = detailsDiv.find( 'li', {'class' : 'release-date'} )
    if releaseDateDiv: appDetails['release_date'] = releaseDateDiv.getText()

    languageDiv = detailsDiv.find( 'li', {'class' : 'language'} )
    if languageDiv: appDetails['language'] = languageDiv.getText().split()

    contentRatingDiv = detailsDiv.find( 'div', {'class' : 'app-rating'} )
    if contentRatingDiv: appDetails['content_rating'] = contentRatingDiv.getText()

    contentRatingReasonDiv = detailsDiv.find( 'list app-rating-reasons' )
    if contentRatingReasonDiv: appDetails['content_rating_reason'] = [li.getText() for li in contentRatingReasonDiv.findAll( 'li' )]

    compatibilityDiv = detailsDiv.find( 'p' )
    if compatibilityDiv: appDetails['compatibility'] = compatibilityDiv.getText()

    customerRatingDivs = detailsDiv.findAll( 'div', {'class' : 'rating', 'role': 'img'} )
    if customerRatingDivs:
        customerRating = customerRatingDivs[-1].get( 'aria-label' ).split( ',' )
        appDetails['rating'] = customerRating[0].strip()
        appDetails['reviewers'] = customerRating[1].strip()

    appLinksDiv = soup.find( 'div', {'class' : 'app-links'} )
    if appLinksDiv:
        for link in appLinksDiv.findAll( 'a', {'class' : 'see-all'} ):
            text = link.getText()
            href = link.get( 'href' )
            if text.endswith( 'Web Site' ): appDetails['developer_wesite'] = href
            elif text.endswith( 'Support' ): appDetails['support'] = href
            elif text.endswith( 'Agreement' ): appDetails['license'] = href

    apps_discovered.append( appUrl )

    return appDetails

def closeFileHandlers( fileHandlers ):
    for v in fileHandlers.values():
        v.close()

if __name__ == '__main__':
    itunesStoreUrl = 'https://itunes.apple.com/us/genre/ios/id36?mt=8'
    mainPage = getPageAsSoup( itunesStoreUrl )
    allCategories = []
    for column in ['list column first', 'list column', 'list column last']:
        columnDiv = mainPage.find( 'ul', {'class' : column} )
        allCategories.extend( aDiv.get( 'href' ) for aDiv in columnDiv.findAll( 'a', href = re.compile( '^https://itunes.apple.com/us/genre' ) ) )

    for category, alphabet in [( x, y ) for x in allCategories for y in string.ascii_uppercase]:
        getApps( category + '&letter=' + alphabet )

    fileHandlers = {}
    count = 100
    while apps_pending:
        if count == 0:
            saveState()
            count = 100
        count = count - 1

        app = apps_pending.pop()
        if not app: continue

        try:
            app_data = getAppDetails( app )
        except Exception as e:
            print( app, e )
            exit( 1 )

        if not app_data:
            continue

        if not app_data['category']: app_data['category'] = 'uncategorized'

        if app_data['category'].lower() not in fileHandlers:
            fileHandlers[app_data['category'].lower()] = codecs.open( '_'.join( ["apple_appstore", app_data['category'].lower()] ), 'ab', character_encoding, buffering = 0 )
            apps_categories[app_data['category'].lower()] = 0
        apps_categories[app_data['category'].lower()] = apps_categories[app_data['category'].lower()] + 1
        fileHandler = fileHandlers[app_data['category'].lower()]
        try:
            fileHandler.write( json.dumps( app_data ) + "\n" )
        except Exception as e:
            print( e )

    saveState()
    closeFileHandlers( fileHandlers )
