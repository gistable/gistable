# App Store playing

import urllib, urllib2, json, plistlib

###
# Utility function for performing an iTunes-style search

def perform_itunes_search(api_url, query_list=[]):
    query_str = urllib.urlencode(query_list)
    response_handle = urllib2.urlopen('https://itunes.apple.com/%s?%s' % (api_url, query_str))
    response = json.loads(response_handle.read())
    response_handle.close()
    return response

# Utility function for parsing iTunes-style search results for Mac apps

def parse_itunes_result(a_result):
    app_info = {'name': a_result['trackName'],
                'size': int(a_result['fileSizeBytes']),
                'CFBundleIdentifier': a_result['bundleId'],
                'CFBundleShortVersionString': a_result['version'],
                'adam-id': a_result['trackId'],
                'installed-version-identifier': 0}
    return app_info

###
# These two functions are good if you know only partial information about single apps.
# However, the third function is better if you know the right information - in that it can batch lookup

# Look up an application by bundle ID

def lookup_app_bundle_id(bundle_id, raw_result=False):
    response = perform_itunes_search('en/lookup', query_list=[('bundleId', bundle_id)])
    if response['resultCount'] > 0:
        if raw_result:
            # Return the data the app store provided, in its entirety
            return response
        # Otherwise assume the first hit is what we want and return information relevant to updates
        return parse_itunes_result(response['results'][0])

# Lookup an application by name
# This is much less reliable than the bundle ID lookup, avoid when possible

def lookup_app_name(app_name, raw_result=False):
    response = perform_itunes_search('search', query_list=[('term', app_name), ('media', 'software'), ('entity', 'macSoftware')])
    if response['resultCount'] > 0:
        if raw_result:
            # Return the data the app store provided, in its entirety
            return response
        # Otherwise assume the first hit is what we want and return information relevant to updates
        return parse_itunes_result(response['results'][0])

###
# This function uses the Mac App Store update checker mechanism.
# It can accept a batch collection of apps to lookup information for.
# It works best with information directly from the receipts and bundle of the application itself.
# Specifically, if it can extract the App Store installed version identifier, a response for that application
# will only be generated if the version is older than (or not found in) the newest version in the version history
# known by the App Store.
# For information on extracting this from the receipts of apps, check my project here:
# https://github.com/pudquick/pyMASreceipt/blob/master/pyMASreceipt.py
# If you pass '0' for the installed-version-identifier, you will always get a result for the app from the App Store
# update mechanism, which includes the latest installed-version-identifier (and all prior ones)

def check_app_updates(app_info_list, raw_result=False):
    # This function expects a list of dicts with, at a minimum, the 'adam-id' key set
    # This ID is the unique product identifier for an app on the App Store and can be found in the store URL
    # when viewing the app's page in a web browser, like so:
    # https://itunes.apple.com/us/app/evernote/id406056744
    #                                            ^^^^^^^^^
    # The other 3 keys that will be passed in the search are: CFBundleIdentifier, CFBundleShortVersionString, and
    # installed-version-identifier (explained earlier). Lack of any of these keys will result in a filler value
    # being provided which, as long as the adam-id is present, the App Store update mechanism doesn't seem to
    # care about.
    update_url = 'https://su.itunes.apple.com/WebObjects/MZSoftwareUpdate.woa/wa/availableSoftwareUpdatesExtended'
    request = urllib2.Request(update_url)
    # Headers #
    # This sets us to the US store. See:
    # http://blogs.oreilly.com/iphone/2008/08/scraping-appstore-reviews.html
    # http://secrets.blacktree.com/edit?id=129761
    request.add_header('X-Apple-Store-Front', '143441-1,13')
    # This indicates we're sending an XML plist
    request.add_header('Content-Type', 'application/x-apple-plist')
    # This seems to be the minimum string to be recognized as a valid app store update checker
    # Normally, it's of the form: User-Agent: MacAppStore/1.3 (Macintosh; OS X 10.9) AppleWebKit/537.71
    request.add_header('User-Agent', 'MacAppStore')
    # Build up the plist
    local_software = []
    for an_app in app_info_list:
        app_entry = {'CFBundleIdentifier': an_app.get('CFBundleIdentifier', '.'),
                     'CFBundleShortVersionString': an_app.get('CFBundleShortVersionString', '0'),
                     'adam-id': an_app['adam-id'],
                     'installed-version-identifier': an_app.get('installed-version-identifier', 0)}
        local_software.append(app_entry)
    plist_dict = {'local-software': local_software}
    plist_str = plistlib.writePlistToString(plist_dict)
    request.add_data(plist_str)
    # Build the connection
    response_handle = urllib2.urlopen(request)
    response = response_handle.read()
    response_handle.close()
    # Currently returning the raw response
    # Initial analysis:
    # - It appears that applications that need updating will be under the 'incompatible-items' key
    # - 'version-external-identifiers' is a list of historical versions, in order
    # - 'version-external-identifier' is the current version
    # - 'current-version' is the CFBundleShortVersionString
    # - 'bundle-id' is the CFBundleIdentifier
    # - 'preflight' is a *very* interesting 'pfpkg'. See details at bottom.
    return plistlib.readPlistFromString(response)

"""
Details regarding .pfpkg type:
Non-standard package format, but still a xar archive (just no bom inside). Appears to contain a single "Distribution"
file which an example is included below.
---
<?xml version="1.0" encoding="utf-8" standalone="no"?>
<installer-gui-script minSpecVersion="2">
    <pkg-ref id="com.evernote.Evernote">
        <bundle-version>
            <bundle CFBundleShortVersionString="5.4.3" CFBundleVersion="402230" id="com.evernote.Evernote" path="Evernote.app"/>
        </bundle-version>
    </pkg-ref>
    <product id="com.evernote.Evernote" version="5.4.3"/>
    <title>Evernote</title>
    <options customize="never" require-scripts="false" hostArchitectures="x86_64,i386" productKBytes="47573"/>
    <volume-check>
        <allowed-os-versions>
            <os-version min="10.6.6"/>
        </allowed-os-versions>
    </volume-check>
    <choices-outline>
        <line choice="default">
            <line choice="com.evernote.Evernote"/>
        </line>
    </choices-outline>
    <choice id="default" title="Evernote" versStr="5.4.3"/>
    <choice id="com.evernote.Evernote" title="Evernote" visible="false" customLocation="/Applications">
        <pkg-ref id="com.evernote.Evernote"/>
    </choice>
    <pkg-ref id="com.evernote.Evernote" version="5.4.3" onConclusion="none" installKBytes="157335">#com.evernote.Evernote.pkg</pkg-ref>
</installer-gui-script>
----

Additional useful URLs:

Cookie analysis from raw headers sent via Mac App Store app:
mzf_odc = x-apple-application-site
mzf_in = x-apple-application-instance
ns-mzf-inst = unique transaction/record handled by instance (?)
X-Dsid = your unique Apple ID numeric identifier (verifiable under Profile page under dev center when logged in)
Pod=44; itspod=44   - unsure

X-Apple-TZ: 
Apparently the x-apple-tz header is UTC offset *60 *60. according to https://github.com/cancan101/xbmc-itunesu/blob/master/TunesViewerBase.py
"""

### New! Search your machine for the App Store information, no need to directly parse receipts

from Foundation import NSMetadataQuery, NSPredicate, NSRunLoop, NSDate

def find_app_store_apps(dirlist=None):
    query = NSMetadataQuery.alloc().init()
    query.setPredicate_(NSPredicate.predicateWithFormat_('(kMDItemAppStoreHasReceipt = "1")'))
    if dirlist:
        query.setSearchScopes_(dirlist)
    query.startQuery()
    runtime = 0
    maxruntime = 20
    while query.isGathering() and runtime <= maxruntime:
        runtime += 0.3
        NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.3))
    query.stopQuery()
    if runtime >= maxruntime:
        print 'Spotlight search terminated'
    app_details = []
    for an_app in query.results():
        app_metadata = an_app.valuesForAttributes_(an_app.attributes())
        app_dict = {}
        app_dict['CFBundleIdentifier'] = app_metadata['kMDItemCFBundleIdentifier']
        app_dict['CFBundleShortVersionString'] = app_metadata['kMDItemVersion']
        app_dict['adam-id'] = app_metadata['kMDItemAppStoreAdamID']
        app_dict['installed-version-identifier'] = int(app_metadata['kMDItemAppStoreInstallerVersionID'])
        app_details.append(app_dict)
    return app_details

### Then try running this :)

check_app_updates(find_app_store_apps())
