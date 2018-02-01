#!/usr/bin/env python
# Contact: Will Wade willwa.de
# Date: April 2013
# Needs mechanize and pybtex
#
# NB: Little error checking going on in this script
# TO-DO: Check last-download-date of bibtex file later than last-modified date on CUL. ? possible
# 
# With thanks to https://pypi.python.org/pypi/citeulike_api/0.1.3dev for the login part 
import mechanize
import time
from pybtex.database.input import bibtex


# settings
cUser = 'willwade'
cPass = 'imnotstupid'
localDir = '/Users/willwade/Dropbox/Papers/'

class CulError(Exception):
    pass

class CiteULikeReader(object):
 
    MIN_API_WAIT = 5
    
    def __init__(self, user, password, localDir=''):
        """ Start up... """
        self.cUser = user
        self.cPass = password
        self.loggedin = False
        self.getPDFs = True
        self.cites = ''
        self.localDir = localDir
        self.last_api_access = time.time() - self.MIN_API_WAIT
        self.loginToCiteULike()

    def wait_for_api_limit(self, min_wait=0):
        min_wait = max(min_wait, self.MIN_API_WAIT)
        now = time.time()
        elapsed_time = now - self.last_api_access
        if elapsed_time<min_wait:
            time.sleep(min_wait-elapsed_time)
        self.last_api_access = time.time()
 
    def loginToCiteULike(self):
        """
        Handle login. This should populate our cookie jar.
        """
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.browser.addheaders = [
          ("User-agent", 'willwade/willwade@gmail.com citeusyncpy/1.0'),
        ]
        self.browser.open('http://www.citeulike.org/login?from=/')
        self.browser.select_form(name='frm')
        self.browser["username"] = self.cUser
        self.browser["password"] = self.cPass
        self.loggedin = True
                
        self.wait_for_api_limit()
        
        try:
            #handle redirects manually to avoid connection flakiness
            self.browser.set_handle_redirect(False)
            resp = self.browser.submit()
        except mechanize.HTTPError, e:
            #This may not work for gold users. See http://www.citeulike.org/groupforum/2949?highlight=41927#msg_41927 for ideas.. feel free to write
            if e.getcode()!=302 : raise e
            next_page = e.info().getheader('Location')
            if next_page == 'http://www.citeulike.org/' :
                #success
                self.logged_in = True
            elif next_page.find('status=login-failed')>=0:
                raise CulError('Login Failed')
            else:
                err = CulError('Unknown login response')
                err.data = e
                raise err
        finally:
            self.browser.set_handle_redirect(True)
        #return ''.join(response.readlines())
        
    def getBibText(self):
        self.browser.retrieve('http://www.citeulike.org/bibtex/user/'+self.cUser+'?do_username_prefix=0&key_type=4&incl_amazon=0&clean_urls=1&smart_wrap=0&export_attachment_names=t&fieldmap=posted-at:date-added',localDir+self.cUser+'.bib')
    
    def downloadPDFS(self):
        #open a bibtex file
        parser = bibtex.Parser()
        bibdata = parser.parse_file(localDir+self.cUser+'.bib')

        #loop through the individual references
        for bib_id in bibdata.entries:
            b = bibdata.entries[bib_id].fields
            try:
                filedl = b["citeulike-attachment-1"].split(';')[1].strip()
                file_name = filedl.split('/')[7]
                filedl = 'http://www.citeulike.org'+filedl
                try:
                   with open(localDir+file_name): pass
                except IOError:
                   # Doesn't exist. Download it
                    (filename, headers) = self.browser.retrieve(filedl,localDir+file_name)
                    self.wait_for_api_limit()
            # field may not exist for a reference
            except(KeyError):
                continue
 
            
    
        
cureader = CiteULikeReader(cUser, cPass, localDir)
cureader.getBibText()
cureader.downloadPDFS()