
# coding: utf-8

# In[297]:

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.options.display.max_rows = 2


#take two files, sf_data and new_data and produce files to use for data loads in sf
#files written are dupes, which is for your information and includes all email addresses that exist more than once in sf
#creates, which is a file to use to create new contact records in sf
#updates, which is a file to use to update existing contact records in sf
#beware, which is a file of the new data rows that matched to more than one record in SF.  Deal with these manually.
#


#create cleaned_new_data, a dataframe to hold the new data, but with the email addresses lowercase
cleaned_new_data=pd.read_csv('/Users/annacrotty/Desktop/for_python/new_data.csv')


# In[298]:

#change cleaned_new_data's consumer_email column to be the previous values but lower case
cleaned_new_data['consumer_email']=cleaned_new_data['consumer_email'].str.lower()


# In[299]:

#now separate sf data into uniques and dupes
sf_data = pd.read_csv('/Users/annacrotty/Desktop/for_python/sf_report.csv')


# In[300]:

#create dataframe uniques for all the rows with unique consumer_email
uniques = sf_data.drop_duplicates('consumer_email')


# In[301]:

sf_data = pd.read_csv('/Users/annacrotty/Desktop/for_python/sf_report.csv')
#find the duplicates and make take_last true

sf_data.duplicated(['consumer_email'], take_last=True)


# In[302]:

#step to find rows with unique consumer_email
sf_data.duplicated(['consumer_email'], take_last=True)|sf_data.duplicated(['consumer_email'])


# In[303]:

#next step in finding those unique consumer_emails
sf_data[sf_data.duplicated(['consumer_email'], take_last=True) | sf_data.duplicated(['consumer_email'])]


# In[304]:

#create dataframe dupes and populate it with rows that have consumer_email that is not unique
#note that this only gives you one instance of the dupe
#problem is that this is making consumer_email the index rather than the numbers that I had before.

dupes = sf_data[sf_data.duplicated(['consumer_email'], take_last=True) | sf_data.duplicated(['consumer_email'])].groupby(('consumer_email')).min()


# In[305]:

#write a file with all the dupes
dupes.to_csv('/Users/annacrotty/Desktop/for_python/dupes.csv')


# In[306]:

#totally embarassing kludge.  I tried to merge dupes and uniques without this step but seemed to have dupes that 
#was a series and not a dataframe, and I'm too new to python and pandas to figure out the more elegant solution.
#so by using groupby.min, I've reduced the dimension to a series.  While this is absolutely the output I want
#I still need a dataframe, not a series.  

dupes = pd.read_csv('/Users/annacrotty/Desktop/for_python/dupes.csv')
dupes


# In[307]:

#delete the column contact id in dupes, it doesn't help you because you don't have the contact ids of the dupes
del dupes['Contact Id']


# In[308]:

#add a column called is_dupe and mark all the values true
dupes['is_dupe']="true"


# In[309]:

#merge uniques and dupes so uniques will have a value indicating if they're dupes
uniques=uniques.merge(dupes, right_on='consumer_email', left_on='consumer_email', how='left')


# In[310]:

#merge cleaned_new_data and uniques
merged_data=cleaned_new_data.merge(uniques, right_on='consumer_email', left_on='consumer_email', how='left')


# In[311]:

#no match between uniques and the new data, these are the creates
#write the file of creates

merged_data[(merged_data['Contact Id'].isnull())].to_csv('/Users/annacrotty/Desktop/for_python/creates.csv')


# In[312]:

#the rows of merged )data that have a value for Contact Id are a first pass to get the updates

updates = merged_data[(merged_data['Contact Id'].notnull())]


# In[313]:

#the ones that also have null value for is_dupe are the final list of updates -
#write the updates file

updates[(updates['is_dupe'].isnull())].to_csv('/Users/annacrotty/Desktop/for_python/updates.csv')


# In[314]:

#and of course if I could do the previous in one step I could do this in one step, as well

beware = merged_data[(merged_data['Contact Id'].notnull())]


# In[315]:

beware[(beware['is_dupe'].notnull())].to_csv('/Users/annacrotty/Desktop/for_python/beware.csv')

