import Skype4Py 

def Commands(message, status):
    if status == 'SENT' or (status == 'RECEIVED'):
    	print message.Body

skype = Skype4Py.Skype()
skype.OnMessageStatus = Commands
skype.Attach()
while True:
    pass