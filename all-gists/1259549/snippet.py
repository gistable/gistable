import sys, time, os
from mechanize import Browser

LOGIN_URL = 'http://www.example.com/login'
USERNAME = 'DavidMertz'
PASSWORD = 'TheSpanishInquisition'
SEARCH_URL = 'http://www.example.com/search?'
FIXED_QUERY = 'food=spam&' 'utensil=spork&' 'date=the_future&'
VARIABLE_QUERY = ['actor=%s' % actor for actor in
                  ('Graham Chapman',
                   'John Cleese',
                   'Terry Gilliam',
                   'Eric Idle',
                   'Terry Jones',
                   'Michael Palin')]

def fetch():
    result_no = 0                 # Number the output files
    br = Browser()                # Create a browser
    br.open(LOGIN_URL)            # Open the login page
    br.select_form(name="login")  # Find the login form
    br['username'] = USERNAME     # Set the form values
    br['password'] = PASSWORD
    resp = br.submit()            # Submit the form

    # Automatic redirect sometimes fails, follow manually when needed
    if 'Redirecting' in br.title():
        resp = br.follow_link(text_regex='click here')

    # Loop through the searches, keeping fixed query parameters
    for actor in in VARIABLE_QUERY:
        # I like to watch what's happening in the console
        print >> sys.stderr, '***', actor
        # Lets do the actual query now
        br.open(SEARCH_URL + FIXED_QUERY + actor)
        # The query actually gives us links to the content pages we like,
        # but there are some other links on the page that we ignore
        nice_links = [l for l in br.links()
                      if 'good_path' in l.url
                      and 'credential' in l.url]
        if not nice_links:        # Maybe the relevant results are empty
            break
        for link in nice_links:
            try:
                response = br.follow_link(link)
                # More console reporting on title of followed link page
                print >> sys.stderr, br.title()
                # Increment output filenames, open and write the file
                result_no += 1
                out = open(result_%04d' % result_no, 'w')
                print >> out, response.read()
                out.close()
            # Nothing ever goes perfectly, ignore if we do not get page
            except mechanize._response.httperror_seek_wrapper:
                print >> sys.stderr, "Response error (probably 404)"
            # Let's not hammer the site too much between fetches
                           time.sleep(1)
