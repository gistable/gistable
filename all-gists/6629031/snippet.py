import mechanize
from bs4 import BeautifulSoup
from datetime import datetime

TGT_DATE = 'MONTH DAY, YEAR' #i.e. 'September 30, 2014'
OFFICE_ID = '503' # officeid for SF DMV. See HTML code for other office ids
NUMBERITEMS = 'Num' # number of tasks for dmv; should be between 1-3
FIRSTNAME = 'FIRST_NAME'
LASTNAME = 'LAST_NAME'
# Number looks like (TELAREA) TELPREFIX-TELSUFFIX
TELAREA = '111'
TELPREFIX = '111'
TELSUFFIX = '1111'

form_url = 'https://www.dmv.ca.gov/foa/clear.do?goTo=officeVisit&localeName=en'
tgt_date = datetime.strptime(TGT_DATE,'%B %d, %Y')

# Browser
br = mechanize.Browser()
br.open(form_url)
br.select_form(name="ApptForm")
br['officeId']=[OFFICE_ID]
br['numberItems']=[NUMBERITEMS]
# br['taskDL']=['true'] # un-comment if it's an appt related to a license
# br['taskVR']=['true'] # un-comment if it's an appt related to a vehicle
br['firstName'] = FIRSTNAME
br['lastName'] = LASTNAME
br['telArea'] = TELAREA
br['telPrefix'] = TELPREFIX
br['telSuffix'] = TELSUFFIX

result = br.submit()
result_html =  br.response().read()
soup = BeautifulSoup(result_html)
results = soup.findAll('p',class_="alert")

for result in results:
    if ('2013' in result.get_text()) or ('2014' in result.get_text()):
      
        appt_text = result.get_text()
        print "Earliest Appointment found is %s" %(appt_text)
        appt_date = datetime.strptime(appt_text,'%A, %B %d, %Y at %I:%M %p')

        if appt_date <= tgt_date:
            print "Congratulations! You've found a date earlier than your target. Scheduling the appointment..."
            br.select_form(nr=4)
            br.submit()

            print "Confirming the appointment..."
            br.select_form(nr=4)
            br.submit()

            br.select_form(nr=3)
            print br #print out relevant info related to the appointment
            return

        else:
            print "Sorry there is no appointment available before your target: %s" %(TGT_DATE)
            return
