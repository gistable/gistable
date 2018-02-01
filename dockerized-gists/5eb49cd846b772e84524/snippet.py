# Pythonista script to create a Launch Center Pro action with all my
# updated grocery lists.
# Author: Aaron Bach
# www: http://www.bachyaproductions.com/

import json
import os
import sys
import urllib
import urllib2
import webbrowser

# USER VARIABLES TO EDIT:
TRELLO_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
BOARD_SHORTCODE = 'xxxxxxxx'

# -------------------------

# Local filepaths:
PYTHONISTA_DOC_DIR = os.path.expanduser('~/Documents')
TOKEN_DIR = os.path.join(PYTHONISTA_DOC_DIR, 'tokens')
TOKEN_FILEPATH = os.path.join(TOKEN_DIR, 'TrelloGroceries.token')

# Trello API URLs:
TRELLO_REQUEST_URL = 'https://trello.com/1/authorize?key=' + TRELLO_KEY + '&name=Grocery+Lists&expiration=never&response_type=token'
TRELLO_BASE_URL = 'https://api.trello.com/1/boards'

# Misc.:
VERBOSE_LOGGING = False

def get_token():
    if os.path.exists(TOKEN_FILEPATH):
        # If a token already exists, use it:
        token_file = open(TOKEN_FILEPATH)
        token = token_file.read()
        token_file.close()
        verbose_log('Reusing existing token: ' + token)
        return token
    else:
        # If a token doesn't exist, go through the
        # process of getting a new one:
        verbose_log('Setting up a new token...')
        return setup_new_token()

def setup_new_token():
    print ">>> I'm going to open Trello so that you can authorize the Grocery Stores application."
    print '>>> Once authorized, copy the token and return to this console; paste it and hit RETURN.'
    webbrowser.open(TRELLO_REQUEST_URL)
    token = raw_input()

    # Save this new token for future use:
    token_file = open(TOKEN_FILEPATH, 'w')
    token_file.write(token)
    token_file.close()

    verbose_log('Saving new token: ' + token)

    # Return the token, as well, so that the functions
    # can chain together correctly:
    return token

def verbose_log(m):
    if VERBOSE_LOGGING:
        print '\n(DEBUG) ' + m + '\n'

def main():
    global VERBOSE_LOGGING
    if '-v' in sys.argv:
        VERBOSE_LOGGING = True

    # If it doesn't exist, create the token directory:
    if not os.path.exists(TOKEN_DIR):
        os.mkdir(TOKEN_DIR)

    # Note that a passed in token might include a newline;
    # safest route is to strip it off here.
    token = get_token().strip()

    # API call to get grocery lists:
    list_url = (TRELLO_BASE_URL + '/'
               + BOARD_SHORTCODE
               + '/lists?&key=' + TRELLO_KEY
               + '&token=' + token + '&fields=name')

    try:
        resp = urllib2.urlopen(list_url)
        grocery_dicts = json.loads(resp.read())

        # If the user passes in a -s flag, sort the grocery store names
        # in ascending alphabetical order.
        if '-s' in sys.argv:
            grocery_dicts.sort(key=lambda k: k['name'])

        # Construct a list of grocery store ID/name combinations
        # (in the format that an LCP list requires):
        list = ''
        for i in grocery_dicts:
            list += '|' + i['name'] + '=' + i['id']

        # Construct the URL that will allow LCP to impor this new action:
        lcp_url = 'trello://x-callback-url/createCard?shortlink=' + BOARD_SHORTCODE + '&name=[prompt:Item]&list-id=[list:Grocery Stores' + list + ']&x-success={{launch:}}'

        # Finally, launch the URL to import the action into LCP.
        webbrowser.open('launch://import?url=' + urllib.quote(lcp_url))
    except Exception, e:
        verbose_log('Dumping variables:\nLIST URL: ' + list_url + '\nKEY: ' + TRELLO_KEY + '\nTOKEN: ' + token)

        print 'There was an error: ' + str(e)
        print 'Your token might have expired.'
        new_token_response = raw_input('Do you want to attempt to get a new one? [y/N] ')

        if new_token_response.lower() == 'y':
            setup_new_token()
            print 'New token created. Try running the script again.'

if __name__ == '__main__':
    main()