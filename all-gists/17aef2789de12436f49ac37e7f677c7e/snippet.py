# -*- coding: utf-8 -*-
"""
Created on Fri Jun 02 17:02:32 2017
@author: Vangelis@logical-invest.com
This script will pull the symbols from your specified Amibroker database and download historical EOD dividend adjusted data from Tiingo.com and will store them 
in a folder (Destop/Data/TiingoEOD) as csv files, one for each stock (APPLE.csv SPY.csv, etc)
It will then attempt to open Amibroker and import the csv files.
You need:
1. To add your own Token number you will get when you register at Tiingo.com (line 51)
2. Specify the Amibroker database you want updated (line 99)

Use as an example. Please modify to your needs
"""

import requests
import time
from bs4 import BeautifulSoup
import json
import os
from win32com.client import Dispatch

#Get todays date in Y-m-d format to use in the Tiingo API call
dateToday = str(time.strftime("%Y-%m-%d"))


#Set the paths to where the data will be stored
#In this example we will create a folder here: Desktop/Data/TiingoEOD
# and store the csv files there

desktop = os.path.expanduser("~/Desktop/")
dataPath=os.path.join(desktop,'Data/TiingoEOD/')

#If no such folder exists, create an empty folder
if not os.path.exists(dataPath):
    os.mkdir(dataPath)
    print 'creating Directory ...'+dataPath
    


def TiingoDailyDatatoCSV(symbol):
    """
    This function will download EOD data from Tiingo.com
    and write to a csv file called nameOfSymbol.csv
    """
    
   # symbol="TLT"
    symbolFile=os.path.join(dataPath,symbol+".csv")
    
    headers = {
           'Content-Type': 'application/json',
           'Authorization' : 'Token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
           }
           
    print "donwloading",symbol, "..."
    
    try:
        response = requests.get("https://api.tiingo.com/tiingo/daily/" + symbol + "/prices?startDate=2000-1-1&endDate="+dateToday,headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        dic = json.loads(soup.prettify())

        row=""
        for i in range(len(dic)):
            ##To convert from 2017-06-01T00:00:00.000Z
            row= row+"\n" + str(dic[i]['date'].split('T')[0]) + "," + str(dic[i]['adjOpen']) + "," +  str(dic[i]['adjHigh']) + "," +  str(dic[i]['adjLow']) + "," + str(dic[i]['adjClose']) + "," + str(dic[i]['adjVolume'])
        
        f = open(symbolFile,"w") 
        f.write(row)
        f.close()
        
        print "finished writing ",symbol,"csv file."
        
    except:
        print "error downloading ",symbol
        
#############################
#--------------------START -------------
    
#This is the import definitions for the csv files             
ABImportDef="$FORMAT Date_YMD, Open, High, Low, Close, Volume, Skip \n$SKIPLINES 1 \n$SEPARATOR , \n$CONT 1 \n$GROUP 255 \n$AUTOADD 1 \n$DEBUG 1"
#print ABImportDef

print "Starting Amibroker import..."


#This is where the format definition file should be. If there is not one already, create one
AB_format_file_path='C:/Program Files/AmiBroker/Formats/TiingoEOD.format'
if not os.path.exists(AB_format_file_path):
    print 'I will create an import file for Amibroker: ',AB_format_file_path, '...'
    defFile = open(AB_format_file_path,"w") 
    defFile.write(ABImportDef)
    defFile.close()
    
data_folders = [
                (dataPath, "TiingoEOD.format")
               ]
               
    
# Create AmiBroker object and specify the Amibroker Database to load
ab = Dispatch("Broker.Application")
ab.LoadDatabase('C:/Program Files/AmiBroker/LiveSystemsData') #Customize

#Get tickers from Amibroker into a list
Qty = ab.Stocks.Count
TickerList=[""]
	
for i in range(Qty): 
    ticker=ab.Stocks( i ).Ticker
    if ticker[0] != "~" and ticker[0] != "^":
       TickerList.append(ab.Stocks( i ).Ticker)
       
print TickerList       
       
##---------------Download all tickers and write to csv
       
for s in TickerList:
    TiingoDailyDatatoCSV(s)
 
#--Import csv

for (data_folder,format_file) in (data_folders):
    for file in os.listdir(data_folder):
        if file[-3:].lower() == "csv":
            print "Importing to AB:", file, "using:", format_file
            ab.Import(0, data_folder + "\\" + file, format_file)
ab.SaveDatabase()
print 'Finished Import'
Sign up for free to join this conversation on GitHub. Already have an account? Sign in to comment
Contact GitHub API Training Shop Blog About
© 2017 GitHub, Inc. Terms Privacy Security Status Help