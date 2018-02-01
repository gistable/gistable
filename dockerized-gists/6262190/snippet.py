# Copyright (c) 2013, Andrea Grandi and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#       1) Redistributions of source code must retain the above copyright notice, 
# 	   this list of conditions and the following disclaimer.
#
# 	2) Redistributions in binary form must reproduce the above copyright notice, 
# 	   this list of conditions and the following disclaimer in the documentation 
# 	   and/or other materials provided with the distribution.
#
# 	3) Neither the name of the WorkshopVenues nor the names of its contributors may 
# 	   be used to endorse or promote products derived from this software without 
# 	   specific prior written permission.
#		
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Credits: this script is based on an example from Michael Richman (@mrwoofster)
# available originally here http://mrwoof.tumblr.com/post/1004514567/using-google-python-api-to-get-rows-from-a-google
#
# Requirements: sudo pip install gdata
#
# Description: this script assume that you have a spreadsheet formatted like this:
# FirstName   - LastName    - Telephone
# John        - Doe         - 123446788
#
####################################################################################

import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db
import logging
import socket

gd_client = gdata.spreadsheet.service.SpreadsheetsService()

# Set the email to your Google account email
gd_client.email = 'youremail@gmail.com'

# Set the password to your Google account password. Please note that if you have 
# enabled the 2-steps authentication in Google you will have to generate a 
# password for this script.
gd_client.password = '******************'

try:                    
    gd_client.ProgrammaticLogin()
except socket.sslerror, e:
    logging.error('Spreadsheet socket.sslerror: ' + str(e))

# key: is the "key" value that you see in the url bar of the browser once you 
# open a Google Docs spreadsheet
key = '**************************************************'

# This is the worksheet ID: the default name of the first sheet is "od6"
wksht_id = 'od6'

try:
    feed = gd_client.GetListFeed(key, wksht_id)
except gdata.service.RequestError, e:
    logging.error('Spreadsheet gdata.service.RequestError: ' + str(e))
except socket.sslerror, e:
    logging.error('Spreadsheet socket.sslerror: ' + str(e))

for row_entry in feed.entry:
    record = gdata.spreadsheet.text_db.Record(row_entry=row_entry)
    print "%s,%s,%s" % (record.content['firstname'], record.content['lastname'], record.content['telephone'])
