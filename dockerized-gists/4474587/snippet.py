import os
from dateutil import parser
import pandas as pd
import numpy as np

#Script to extract Timestamp, From, and Subject from BLDG-SIM Email Archive. Best results if used from IPython terminal
#then plotted and exported data as desired

#Path to files downloaded from http://lists.onebuilding.org/pipermail/bldg-sim-onebuilding.org/
path = '/BLDG-SIM Analysis/textfiles'
filelist = os.listdir(path)
os.chdir(path)
DataList = []

#Open all the files one at a time
for file in filelist:
    i=0
    openfile = open(file)
    linelist = [line for line in openfile.readlines()]
    linelistmax=len(linelist)

    #Iterate through each file and find the From:, Date:, and Subject: for each email
    while i < linelistmax:
        try:
            if linelist[i][:5] == 'From:':
                if linelist[i+2][:8] == 'Subject:':
                    WholeDate = parser.parse(linelist[i+1][6:]).replace(tzinfo=None)
                    Date = WholeDate.date()
#                    YearMonth = WholeDate.replace(day=0)
                    DataEntry = (linelist[i][5:],Date,WholeDate,linelist[i+2][19:])
                    DataList.append(DataEntry)
        except ValueError:
            print 'Bad Date: '+linelist[i+1]
        i+=1
    print "Finished Loading "+file
    
#Use pandas data manipulation capabilities to aggregate, etc
bldgsimdata = pd.DataFrame(data=DataList,columns=['From','Date','DateTime','Subject'])
bldgsimdata = bldgsimdata.sort(columns='DateTime')

NumberPerDay = bldgsimdata.groupby('Date').size()
NumberPerDayIndex = pd.DatetimeIndex(NumberPerDay.index)
NumberPerDay=NumberPerDay.reindex(index=NumberPerDayIndex)
NumberPerMonth = NumberPerDay.resample('M',how='sum')

AggSubjects = bldgsimdata.groupby('Subject').size()

PeopleFreq = bldgsimdata.groupby('From').size()
PeopleFreq = PeopleFreq.sort()

monthgrouped = NumberPerDay.groupby(lambda x: x.month)
monthlystats = monthgrouped.agg({'monthlysum': np.sum, 'dailymean': np.mean})

os.chdir('/Users/millerc/Dropbox/CODE/BLDG-SIM Analysis/')


