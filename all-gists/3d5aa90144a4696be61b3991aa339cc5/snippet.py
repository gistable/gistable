import win32com.client

items = []

def encodeit(s):
    if isinstance(s, str):
        return unicode(s, 'utf-8')
    else:
        return s

def extract():
  
  outlook  = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
  inbox    = outlook.GetDefaultFolder(6)  # "6" refers to the inbox
  messages = inbox.Items
  message  = messages.GetFirst()
  
  
  while message:
      
      try:
          d = dict()
          d['Subject'] = encodeit(getattr(message, 'Subject', '<UNKNOWN>'))
          d['SentOn']  = encodeit(getattr(message, 'SentOn', '<UNKNOWN>'))
          d['EntryID'] = encodeit(getattr(message, 'EntryID', '<UNKNOWN>'))
          d['Sender']  = encodeit(getattr(message, 'Sender', '<UNKNOWN>'))
          d['Size']    = encodeit(getattr(message, 'Size', '<UNKNOWN>'))
          d['Body']    = encodeit(getattr(message, 'Body', '<UNKNOWN>'))
          items.append(d)

      except Exception as inst:
          print "Error processing mail"
  
      message = messages.GetNext()
      
def showMessage():
  items.sort(key=lambda tup: tup['SentOn']) 
  
  for i in items:
    print i["SentOn"], i["Subject"]
    
extract()
showMessage()