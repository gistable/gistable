import csv
import os
import re
import dateutil
import pandas as pd
from urlparse import urlparse

log_path = ''
# parsing code: http://ferrouswheel.me/2010/01/python_tparse-fields-in-s3-logs/
log_entries = []
for log in os.listdir(log_path):
    r = csv.reader(open(log_path + log), delimiter=' ', quotechar='"')
    for i in r:
        i[2] = i[2] + ' ' + i[3]  # repair date field
        del i[3]
        log_entries.append(i)
# format: http://docs.aws.amazon.com/AmazonS3/latest/dev/LogFormat.html
columns = ['Bucket_Owner', 'Bucket', 'Time', 'Remote_IP', 'Requester',
           'Request_ID', 'Operation', 'Key', 'Request_URI', 'HTTP_status',
           'Error_Code', 'Bytes_Sent', 'Object_Size', 'Total_Time',
           'Turn_Around_Time', 'Referrer', 'User_Agent', 'Version_Id']
df = pd.DataFrame(log_entries, columns=columns)
df = df.mask(df == '-')
df.Time = df.Time.map(lambda x: x[x.find('[') + 1:x.find(' ')])
df.Time = df.Time.map(lambda x: re.sub(':', ' ', x, 1))
df.Time = df.Time.apply(dateutil.parser.parse)
df['Date'] = df.Time.apply(lambda x: x.strftime('%m-%d-%Y'))
df.Key = df.Key.apply(lambda x: re.sub('index\.html', '', x) if x == x else None)
df.Referrer = df.Referrer.apply(lambda x: urlparse(x).hostname if x == x else None)
df.to_csv('log.csv', index=False)
