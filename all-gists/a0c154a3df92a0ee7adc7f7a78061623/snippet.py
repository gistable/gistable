# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:38:13 2017

@author: Ana-Maria.Mocanu
"""

from bs4 import BeautifulSoup
import csv
import os

def process_coordinate_string(list_test):
    """
    Take the coordinate string from the KML file, and break it up into [Lat,Lon,Lat,Lon...] for a CSV row and other columns
    """
    ret = []
    ret.append(list_test[0])              # Name 
    ret.append(list_test[1])              # Description 
    coordstr = list_test[2].rstrip('\n')
    space_splits = coordstr.split(" ")
    #take out the empty values
    space_splits = list(filter(None, space_splits))
#    # There was a space in between <coordinates>" "-80.123...... hence the [1:]
    for split in space_splits[1:]:
        comma_split = split.split(',')
        
        ret.append(comma_split[1])    # lat
        ret.append(comma_split[0])    # lng
        #to test the output: print(ret)
    ret.append(list_test[3])   #Company Name
    return ret

def kml_to_csv(rootDir, kmlFile, csvFile, company_name):
    """
    Open the KML. Read the KML. Open a CSV file. Process a coordinate string to be a CSV row.
    """
    with open(rootDir + kmlFile, encoding='utf8') as f:
        s = BeautifulSoup(f, 'xml')
        with open(rootDir + csvFile, 'w', newline='', encoding='utf8') as csvfile:
            #Define the headers
            header = ['Name', 'Description', 'Latitude', 'Longitude', 'Company Name']
            writer = csv.writer(csvfile)
        
            writer.writerow(header)
            total_list = []
            for placemark in s.find_all('Placemark'):
                #added conditions for no values in child tags
                name = placemark.find('name').string  \
                       if placemark.find('name') is not None  \
                       else 'None'
                description = placemark.find('description').string  \
                              if placemark.find('description') is not None  \
                              else 'None'
                coords = placemark.find('coordinates').string \
                         if placemark.find('coordinates') is not None  \
                         else 'None'
                #create a list for and append values for each row
                list_test = []
                list_test.extend((name.string, description.string, coords.string, company_name))
                total_list.append(process_coordinate_string(list_test))
                #print(coords.string)
                #print(total_list)
            writer.writerows(total_list)

def main():  
    #Define the absolute path
    abs_path = os.path.normpath(os.getcwd() + os.sep + os.pardir)

    kml_to_csv(abs_path, \
               '\\Data_Input\\<your kml file>',\
               '\\Data_Output\\<your csv file>',\
               <Company Name or custom label>)

if __name__ == "__main__":
    main()