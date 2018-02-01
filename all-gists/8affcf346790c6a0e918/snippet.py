# See https://pip.pypa.io/en/latest/installing.html for how to install pip, then:
# pip install simple-salesforce
from simple_salesforce import Salesforce
import string

# To get your SFDC token, see https://help.salesforce.com/apex/HTViewHelpDoc?id=user_security_token.htm
# salesforce_login.txt should contain the following, one per line:
# Your Name
# your_email@sfdc_account.com
# your_password
# your_sfdc_token
with open('salesforce_login.txt') as f:
  se_name, username, password, token = [x.strip("\n") for x in f.readlines()]
sf = Salesforce(username=username, password=password, security_token=token)

accounts = sf.query("select accountid, count(name) from opportunity where opportunity.lead_se__c = '"+se_name+"' group by accountid").items()[2][1]
for account in accounts:
  account_id = account.items()[1][1]
  account_name = sf.query("select name from account where id='"+account_id+"'").items()[2][1][0].items()[1][1]
  cases = sf.query("select casenumber, description, reason, status, priority, problem_type__c, lastvieweddate from case where accountId='"+account_id+"' and isclosed=false").items()[2][1]
  print '---------------------------------'
  print ''
  print 'AccountName: ' + account_name + ' , AccountId: ' + account_id + ' : ' + str(len(cases)) + ' open cases.'
  for case in cases:
    case_number = case.items()[1][1]
    description = case.items()[2][1]
    description = filter(lambda x: x in string.printable, description)
    if description != '': print str(account_name) + ', ' + str(case_number) + ': ' + str(description)