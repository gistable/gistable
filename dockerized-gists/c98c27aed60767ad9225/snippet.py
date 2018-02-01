import urllib2 as url 
import bs4
import pandas as pd
import numpy as np
import re
	   
base_url = 'http://www.yellowpages.com/search?search_terms=coffee&geo_location_terms=Los%20Angeles%2C%20CA'

def get_url_build(base_url,limit):
    
   #initialisation() 
   for i in range(1,limit + 1): 
      url1 = base_url + '&page=' + str(i) 
      print url1  
      soup = get_url_parsed(url1)
      get_url_data(soup)
      write_csv(cols)  
        
def get_url_parsed(url1):   
#This is the dacomment in ipython
   buty = url.urlopen(url1).read()
   soup = bs4.BeautifulSoup(buty) 
   #print soup 
   return soup
  
def get_url_data(soup):   
   g_data = soup.find_all("div",{"class":"info"})
  # print g_data 
   for item in g_data:
      i = 0
      
      try :
         cols['Business_Name'].append(item.contents[0].find_all("a",{"class":"business-name"})[0].text.encode('ascii', 'ignore') )    #Business Name
      except :
            cols['Business_Name'].append(' ') 
      pass
      
      try :  
         cols['Street_Address'].append(item.contents[1].find_all("span",{"itemprop":"streetAddress"})[0].text.encode('ascii', 'ignore') )  #street Address 
      except :
            cols['Street_Address'].append(' ') 
      pass
      
      try :
         cols['Locality'].append(item.contents[1].find_all("span")[2].text.replace(',','').encode('ascii', 'ignore') )  #locality 
      except :
         cols['Locality'].append(' ')
      pass
          
      try :
         cols['Region'].append(item.contents[1].find_all("span")[3].text.encode('ascii', 'ignore') )  #AddressRegion
      except :
         cols['Region'].append(' ')
      pass
          
      try :
         cols['Zipcode'].append(item.contents[1].find_all("span")[4].text.encode('ascii', 'ignore') )  #PostalCode zipcode
      except :
         cols['Zipcode'].append(' ')
      pass
      
      try :
         cols['Contact'].append(item.contents[1].find_all("ul",{"class":"phones"})[0].text.encode('ascii', 'ignore')) #phones number
         
      except :
         cols['Contact'].append(' ') 
      pass
          
      try :
         cols['Website'].append(item.contents[1].find('a', attrs={'href': re.compile("^http://")}).get('href').encode('ascii', 'ignore') )#store website links
      except :
         cols['Website'].append(' ') 
      pass
          
      try : 
         classes = item.contents[1].find('div', {'class':"result-rating"})
         rating  = (classes.get('class')[1] + ' ' + classes.get('class')[2]).strip()
         #print rating
         for key, value in number.items():
            if  key == rating :
             #print value  
              cols['Ratings'].append(value.encode('ascii', 'ignore'))
                  
      except :
          cols['Ratings'].append(' ')
      pass
      #return cols                 
                    
def write_csv(cols):
    
   # print data1
    data1 = pd.DataFrame(cols)#.encode("utf-8")
   #return data
    data1.to_csv("yellowpages_coffee_CA.csv", index=False)
        

if __name__ == '__main__':
        #initialisation()
        cols = {'Business_Name'  : [],
                'Street_Address' : [],
                'Locality'       : [],
                'Region'         : [],
                'Zipcode'        : [],
                'Contact'        : [],
                'Website'        : [],
                'Ratings'        : []
               }
        #print cols
        number = {'one':1,
                  'one half':1.5, 
                  'two':2,
                  'two half':2.5,
                  'three':3,
                  'three half':3.5,
                  'four':4,
                  'four half':4.5,
                  'five':5,
                  'five half':5.5}
        data1 = pd.DataFrame()
        #print data1 
        #print '2' 
        
        base_url = 'http://www.yellowpages.com/search?search_terms=coffee&geo_location_terms=Los%20Angeles%2C%20CA'
        limits = raw_input("Enter No of pages to read")
        limits = int(limits)
        get_url_build(base_url,limits)
    
    
    #print data1
      