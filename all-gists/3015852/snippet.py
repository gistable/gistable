#!/usr/bin/env python
# -*- python -*-
#
# Plugin to track account balances on ingdirect.com.au, using selenium gymnastics to log in
#
# E.g.
#    ln -s /usr/share/munin/plugins/ingdirect.py /etc/munin/plugins/ingdirect
#
# Needs (hint: pip install):
#   selenium
#   pyvirtualdisplay (also sudo apt-get install xvfb)
#   simplejson
#   PIL
#
# Needs following minimal configuration in plugin-conf.d/munin-node:
#   [ingdirect]
#   client 9876
#   pin 1234
#   refresh 360 # optional refresh rate in minutes
#
# Author: Roger Barnes  <roger@mindsocket.com.au>

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from simplejson.decoder import JSONDecodeError
from PIL import Image
import StringIO
import re
import hashlib
import base64
import sys
import os
import simplejson
import time

verbose=False

def verboselog(s):
    global plugin_name
    sys.stderr.write(plugin_name+': '+s+'\n')

if not verbose :
    verboselog = lambda s: None

def splat(type, value, tb):
    """Exception hook to fire up pdb if we have a tty"""
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback, pdb
        # we are NOT in interactive mode, print the exception...
        traceback.print_exception(type, value, tb)
        print
        # ...then start the debugger in post-mortem mode.
        pdb.pm()

sys.excepthook = splat

def getcropbox(button):
    """Given a selenium WebElement, return a PIL friendly 
    (left, top, right, bottom) crop box
    including the top frame and padding offsets"""
    topframe = 95
    padding = 6
    xoffset = padding
    yoffset = topframe + padding
    return (
        xoffset + button.location['x'], 
        yoffset + button.location['y'], 
        xoffset + button.location['x'] + button.size['width'], 
        yoffset + button.location['y'] + button.size['height']
    )

def get_balances(driver, path):
    """Given an xpath, extract the account rows and return 
    a list of tuples (account name, balance)"""
    table = driver.find_element_by_xpath(path)
    verboselog(table)
    all_rows = table.find_elements_by_xpath("tbody/tr")
    verboselog(all_rows)

    balances = []
    for row in all_rows[1:-1]:
        cells = row.find_elements_by_tag_name('td')
        balances.append((cells[1].text.strip(), 
                         float(re.findall(r'[0-9.,]+', cells[6].text)[0].replace(',', ''))
                         ))
    return balances

class INGDirect(object):
    # Mapping of PIN digits to md5sums of button images
    nums = {
        '0': '9b1e2f2424bed4698e628bc8efc4d917', 
        '1': '4732bbdd77938edc99bf29b8b9f95ca1', 
        '2': '90d0aa87be7fc3b06250acb1364301e6', 
        '3': 'a4c8204ec0b17e0840cd3c493bfd46b6', 
        '4': '4b5a21179a172e3d0eb631349d1df4d9', 
        '5': '99167e3c333f1d3b6fe78dedb6dd72a0', 
        '6': 'f1f669791224037c38b8239d88528b72', 
        '7': '4374e88a64088bdc988a95dc0abeed76', 
        '8': '9282c5583088f880cda228225b3cf4be', 
        '9': 'a502640945909a81c031caa334febc28', 
        'cancel': '5285990feb6cc21055aae02230ff9d64',
        'clear': 'f7b4cfdcc435dac1213372c511c6f759', 
    }
    
    def __init__(self, client, pin, visible=0):
        # Virtual display setup
        from pyvirtualdisplay import Display
        self.display = Display(visible=visible, size=(800, 800))
        self.display.start()
        
        # Selenium setup
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.base_url = "https://www.ingdirect.com.au"
        self.verificationErrors = []
        
        # Login params
        self.client = client
        self.pin = pin

    def get_balances(self):
        """Main workload, logs in and gets balances"""
        driver = self.driver
        driver.get(self.base_url + "/client/index.aspx")
        #driver.get_screenshot_as_file("/tmp/ingdirect_screenshot.png")
        driver.switch_to_frame('body')
        
        # Type in client number
        driver.find_element_by_id("txtCIF").clear()
        driver.find_element_by_id("txtCIF").send_keys(self.client)
        
        # Get screenshot for extraction of button images
        im = Image.open(StringIO.StringIO(base64.decodestring(driver.get_screenshot_as_base64())))

        barr = {}
        table = driver.find_element_by_xpath("""//*[@id="objKeypad_divShowAll"]/table""")
        all_buttons = table.find_elements_by_tag_name("input")
        
        # Determine md5sum of each button by cropping the screenshot based on element positions
        for button in all_buttons:
            #print "Value is: %s %s %s %s" % (
            #    button.get_attribute("id"), button.get_attribute("src"), button.location, button.size)
            bim = im.crop(getcropbox(button))
            hexid = hashlib.md5(bim.tostring()).hexdigest()
            #bim.save("/tmp/%s-%s.png" % (hexid, button.get_attribute("id")))
            barr[hexid] = button.get_attribute("id")
        
        #print barr
        # Now we know which button is which, enter the PIN
        for char in self.pin:
            #print barr[nums[char]]
            driver.find_element_by_id(barr[self.nums[char]]).click()
            
        driver.find_element_by_id("btnLogin").click()
        
        # We're in! Grab the balances from the Transaction and Savings account sections
        
        balances =  get_balances(driver, """//*[@id="asTrans_gvAccountSummary"]""") + \
                    get_balances(driver, """//*[@id="asSavings_gvAccountSummary"]""")

        return balances
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.quit()
        self.display.stop()

to_key = lambda s: re.sub('[()]', '', s).replace(' ', '_').lower()
  
def print_config(state):
    """Munin config based on current state"""
    verboselog('Printing configuration')
    print('graph_title ING Direct account balances')
    print('graph_vlabel balance')
    print('graph_args --logarithmic --base 1000 --lower-limit 100')
    print('graph_category personal')
    print('graph_info This graph shows the balance of all ING Direct accounts')
    print('graph_total total')
    attributes=[b[0] for b in state['balances']]
    attributes.sort()
    for key in attributes :
        print(to_key(key) + '.label ' + key)
        print(to_key(key) + '.type GAUGE')

if __name__ == "__main__":
    plugin_name=list(os.path.split(sys.argv[0]))[1]
    verboselog('plugins\' UID: '+str(os.geteuid())+' / plugins\' GID: '+str(os.getegid()))
    
    # read state (JSON)
    state = {}
    statepath = os.getenv('MUNIN_STATEFILE', '/tmp/ingdirect-')
    try:
        with open(statepath,'r') as statefile:
            state = simplejson.load(statefile)
    except (IOError, JSONDecodeError):
        pass
    
    # Only get fresh balances every 6 hours (or as configured in munin-node)
    if not 'lastupdate' in state or state['lastupdate'] < time.time() - (os.getenv('refresh', 360) * 60):
        with INGDirect(client=os.getenv('client'), pin=os.getenv('pin')) as client:
            state['lastupdate'] = time.time()
            state['balances'] = client.get_balances()
            with open(statepath,'w') as statefile:
                simplejson.dump(state, statefile)

    verboselog(simplejson.dumps(state))
    
    # Parse arguments
    if len(sys.argv)>1 and sys.argv[1]=="config":
        print_config(state)
        sys.exit(0)

    # Results for munin
    for account, balance in state['balances']:
        print("%s.value %f" % (to_key(account), balance))
