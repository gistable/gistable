# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 18:55:20 2016

@author: cpard
"""
from sqlalchemy import create_engine
import pandas as padas
import numpy as np
import statsmodels.api as sm

engine = create_engine('postgresql://USERNAME:PASSWORD@HOST:PORT/DBNAME')

joinedQuery = """select * from (select  c_campaign_id, rec_list_id, email_address as c_email_address, send_time as c_send_time, c_title from 
(select distinct id as c_campaign_id, recipients_list_id as rec_list_id, send_time, settings_title as c_title from mailchimp_new_campaigns) n 
inner join mailchimp_new_list_members on 
(n.rec_list_id = mailchimp_new_list_members.list_id and mailchimp_new_list_members.timestamp_opt <= n.send_time)) m 
full outer join (select e_campaign_id, e_email_address, sub_settings_title as e_settings_title, action as e_action, e_send_time from (select distinct campaign_id as e_campaign_id, email_address as e_email_address, action from mailchimp_new_report_email_activity where action = 'open') n
 join (select distinct id as sub_c_id, settings_title as sub_settings_title, send_time as e_send_time from mailchimp_new_campaigns) m on (m.sub_c_id = n.e_campaign_id)) k 
on(m.c_campaign_id = k.e_campaign_id and m.c_email_address = k.e_email_address) order by m.c_campaign_id"""

domains = [] # an array acting as an authority list of email addresses that we know 
             # that they are used for personal don't forget to add your own here e.g. ['gmail', 'yahoo', 'outlook']
 
mailCampaignData = padas.read_sql_query(joinedQuery,engine)

def hasOpened(st):
    res = 0    
    if st == 'open':
        res = 1
    return res
     
def isBlog(st):
    res = 0
    if 'New Post' in st:
        res = 1
    return res
   
def isBusiness(st):
    domain = st.split("@")[1]
    res = 1
    for s in domains:
        if s in domain:
            res = 0
            break
    return res

def sendDuringWorkTime(time):
    result = 0
    if time >=9 and time <= 17:
        result = 1
    return result
    
mailCampaignData.c_title.fillna(mailCampaignData.e_settings_title, inplace=True)
mailCampaignData.e_settings_title.fillna(mailCampaignData.c_title, inplace=True)

mailCampaignData.c_send_time.fillna(mailCampaignData.e_send_time, inplace=True)
mailCampaignData.e_send_time.fillna(mailCampaignData.c_send_time, inplace=True)

l = mailCampaignData['e_action'].apply(hasOpened).to_frame(name='opened')

k = mailCampaignData['c_title'].apply(isBlog).to_frame('isBlog')
r = padas.concat([mailCampaignData, l, k], axis=1)

# extract the hour of the day from the date columns we have
extractedHours = padas.DataFrame(padas.DatetimeIndex(r['c_send_time']).hour,index = r.index, columns=['duringWork'])
r = padas.concat([r, extractedHours], axis=1)
r['duringWork'] = r['duringWork'].apply(sendDuringWorkTime)

#deal with any NA values that we might have in our data
r.e_campaign_id.fillna(r.c_campaign_id, inplace=True)
r.e_email_address.fillna(r.c_email_address, inplace=True)

r.c_campaign_id.fillna(r.e_campaign_id, inplace=True)
r.c_email_address.fillna(r.e_email_address, inplace=True)
j = r['e_email_address'].apply(isBusiness).to_frame('businessAddress')
r = padas.concat([r, j], axis=1)

# drop the stuff we do not need any more
r.drop(['rec_list_id','c_campaign_id','c_email_address','c_title','e_campaign_id','e_settings_title','e_action', 'e_send_time', 'c_send_time','c_email_address', 'e_email_address'],axis=1, inplace=True)

# we need to manualy add a value for the intercept for each of the observations, this is 
# a requirement of the libraries we use.
r['intercept']=1.0
train_cols = r.columns[1:]

logit = sm.Logit(r['opened'], r[train_cols])
result = logit.fit()

#print a summary of the fitted model, here we can start interpreting the results
print result.summary()

params = result.params
conf = result.conf_int()
conf['OR'] = params
conf.columns = ['2.5%', '97.5%', 'OR']
#calculate Odd rations together with confidence intervals.
print np.exp(conf)
