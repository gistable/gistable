#Install scipy: http://glowingpython.blogspot.it/2012/05/analyzing-your-gmail-with-matplotlib.html

from imaplib import IMAP4_SSL
from datetime import date,timedelta,datetime
from time import mktime
from email.utils import parsedate
from pylab import plot_date,show,xticks,date2num
from pylab import figure,hist,num2date
from matplotlib.dates import DateFormatter

def getHeaders(address,password,folder,d):
    """ retrieve the headers of the emails from d days ago until now """
    # imap connection
    mail = IMAP4_SSL('imap.gmail.com')
    mail.login(address,password)
    mail.select(folder) 
    # retrieving the uids
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, data = mail.uid('search', None, '(SENTSINCE {date})'.format(date=interval))
    # retrieving the headers
    result, data = mail.uid('fetch', data[0].replace(' ',','), '(BODY[HEADER.FIELDS (DATE)])')
    mail.close()
    mail.logout()
    return data

def diurnalPlot(headers):
    """ diurnal plot of the emails, with years running along the x axis and times of day on the y axis."""
    xday = []
    ytime = []
    for h in headers: 
        if len(h) > 1:
            timestamp = mktime(parsedate(h[1][5:].replace('.',':')))
            mailstamp = datetime.fromtimestamp(timestamp)
            xday.append(mailstamp)
            # Time the email is arrived
            # Note that years, month and day are not important here.
            y = datetime(2010,10,14, mailstamp.hour, mailstamp.minute, mailstamp.second)
            ytime.append(y)
    
    plot_date(xday,ytime,'.',alpha=.7)
    xticks(rotation=30)
    return xday,ytime

def dailyDistributioPlot(ytime):
    """ draw the histogram of the daily distribution """
    # converting dates to numbers
    numtime = [date2num(t) for t in ytime] 
    # plotting the histogram
    ax = figure().gca()
    _, _, patches = hist(numtime, bins=24,alpha=.5)
    # adding the labels for the x axis
    tks = [num2date(p.get_x()) for p in patches] 
    xticks(tks,rotation=75)
    # formatting the dates on the x axis
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))


print 'Fetching emails...'
headers = getHeaders('USERNAME@gmail.com','your_password','inbox',365*2) #or [Gmail]/Sent Mail

print 'Plotting some statistics...'
xday,ytime = diurnalPlot(headers)
dailyDistributioPlot(ytime)
print len(xday),'Emails analysed.'
show()
