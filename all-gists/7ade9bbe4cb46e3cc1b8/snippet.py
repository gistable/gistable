# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import weechat, csv, re, gammu, time, unicodedata

"""
README
======

2015-04-12: v0.1 - Initial/draft/beta version

Installation
------------

$ sudo aptitude install gammu gammu-smsd python-gammu
$ sudo usermod -a -G dialout $USER

$ cp weesms.py ~/.weechat/python/[autoload]

Stop gammu-smsd if it is started:
# /etc/init.d/gammu-smsd stop


Plugin management
-----------------

Load plugin:
/python load python/weesms.py or put the script in python/autoload

Reload plugin:
/python reload weesms

Unload plugin:
/python unload weesms


Phonebook
---------

Default CSV phonebook location: WEECHAT_DIR/python/weesms.csv

Phonebook format is:
bob,+33123456789
alice,+33987654321


Refs:
  - http://wammu.eu/docs/pdf/gammu.pdf
  - https://weechat.org/files/doc/stable/weechat_scripting.en.html
  - https://weechat.org/files/doc/stable/weechat_plugin_api.en.html

"""

SCRIPT_NAME    = "weesms"
SCRIPT_AUTHOR  = "Steeve Barbeau"
SCRIPT_LICENCE = "GPL3"
SCRIPT_VERSION = "0.1"
SCRIPT_DESC    = "Send and receive SMS Text Messages in Weechat"

contacts_dict = {}


def buffer_input_cb(data, buffer, input_data):
  smsbuffer = weechat.buffer_search('python', 'weesms')
  input_data = input_data.decode('utf-8', 'replace')
  r = re.compile("^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$")
  # regex stolen from http://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number/16702965#16702965
  if ':' in input_data:
    contact, _, message = input_data.partition(':')
    if contact in contacts_dict.keys():
      number = contacts_dict[contact]
    else:
      number = contact
    if r.match(number):
      weechat.prnt(smsbuffer, "-> %s: %s" % (contact, unicodedata.normalize('NFKD', message).encode('ascii', 'ignore')))
      send_sms(message.strip(), number)
  return weechat.WEECHAT_RC_OK


def buffer_close_cb(data, buffer):
  # ...
  return weechat.WEECHAT_RC_OK


def reload_contacts_cb(data, buffer, args):
  global contacts
  csv_file = weechat.info_get('weechat_dir', '')+'/python/weesms.csv'
  try:
    contacts_csv = csv.reader(open(csv_file, 'r'))
    weechat.nicklist_remove_group(smsbuffer, contacts)
    contacts = weechat.nicklist_add_group(smsbuffer, '', 'contacts', '', 1)
    for c in contacts_csv:
      weechat.nicklist_add_nick(smsbuffer, contacts, c[0], '', '@', '', 1)
      contacts_dict[c[0]] = c[1]
    weechat.prnt('', "Contacts reload: done")
  except IOError:
    weechat.prnt('', "%sIOError: Unable to access %s file" % (csv_file, weechat.prefix("error")))
    return weechat.WEECHAT_RC_ERROR
  return weechat.WEECHAT_RC_OK


def shutdown_function():
  sm.Terminate()
  return weechat.WEECHAT_RC_OK


def nicklist_init():
  csv_file = weechat.info_get('weechat_dir', '')+'/python/weesms.csv'
  try:
    contacts_csv = csv.reader(open(csv_file, 'r'))
    for c in contacts_csv:
      weechat.nicklist_add_nick(smsbuffer, contacts, c[0], '', '@', '', 1)
      contacts_dict[c[0]] = c[1]
  except IOError:
    weechat.prnt('', "%sIOError: Unable to access %s file" % (csv_file, weechat.prefix("error")))


def gammu_init():
  weechat.prnt('', "Gammu initialization")
  # Create state machine
  sm = gammu.StateMachine()
  # Read gammurc
  sm.ReadConfig()
  # Connect to phone
  sm.Init(5)
  # Enter PIN code if necessary
  if (sm.GetSecurityStatus() == 'PIN'):
    weechat.prnt('', "Setting PIN code")
    sm.EnterSecurityCode('PIN', '0000')
  time.sleep(5)
  weechat.prnt('', "Gammu initialization: done")
  return sm


def send_sms(text, number):
  # Create SMS info structure
  smsinfo = {
    'Class': 1,
    'Unicode': True,
    'Entries':  [
      {
        'ID': 'ConcatenatedAutoTextLong',
        'Buffer': text
      }
    ]}

  # Encode messages
  encoded = gammu.EncodeSMS(smsinfo)

  # Send messages
  for message in encoded:
    message['SMSC'] = {'Location': 1}
    message['Number'] = number

    # Actually send the message
    try:
      sm.SendSMS(message)
    except gammu.ERR_GETTING_SMSC as e:
      weechat.prnt('', "%s%s" % (weechat.prefix("error"), e))
    except gammu.ERR_TIMEOUT as e:
      weechat.prnt('', "%s%s" % (weechat.prefix("error"), e))


def read_sms_cb(data, remaining_calls):
  try:
    status = sm.GetSMSStatus()
  except gammu.ERR_TIMEOUT as e:
    weechat.prnt('', "%s%s" % (weechat.prefix("error"), e))
    return weechat.WEECHAT_RC_ERROR

  remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']
  sms = []
  start = True

  try:
    while remain > 0:
      if start:
        cursms = sm.GetNextSMS(Start=True, Folder=0)
        start = False
      else:
        cursms = sm.GetNextSMS(Location=cursms[0]['Location'], Folder=0)
      remain = remain - len(cursms)
      sms.append(cursms)
  except gammu.ERR_EMPTY:
    pass
 
  data = gammu.LinkSMS(sms)
 
  for x in data:
    v = gammu.DecodeSMS(x)
 
    m = x[0]
    sms_number = m['Number']

    contact = sms_number
    for name, number in contacts_dict.iteritems():
      if number == sms_number:
        contact = name
        break
    if v is None:
      message = unicodedata.normalize('NFKD', m['Text']).encode('ascii', 'ignore')
    else:
      for e in v['Entries']:
        if e['Buffer'] != None:
          message = unicodedata.normalize('NFKD', e['Buffer']).encode('ascii', 'ignore')
    weechat.prnt(smsbuffer, "<- %s: %s" % (contact, message))

    # Delete SMS
    loc = []
    for m in x:
        sm.DeleteSMS(m['Folder'], m['Location'])
  return weechat.WEECHAT_RC_OK


# plugin registration
if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENCE, SCRIPT_DESC, 'shutdown_function', ''):
  # WeeSMS buffer creation
  smsbuffer = weechat.buffer_new('weesms', 'buffer_input_cb', '', 'buffer_close_cb', '')
  weechat.buffer_set(smsbuffer, 'WeeSMS', '- SMS -')

  # Nick list initialization
  contacts = weechat.nicklist_add_group(smsbuffer, '', 'contacts', '', 1)
  nicklist_init()

  # /reload_contacts command
  hook = weechat.hook_command('reload_contacts', "Reload CSV phonebook", '', '', '', 'reload_contacts_cb', '')

  # Initialize Gammu
  sm = gammu_init()

  # SMS check function called every 10 seconds
  weechat.hook_timer(10 * 1000, 0, 0, 'read_sms_cb', '')
