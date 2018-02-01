from selenium import webdriver
from selenium import selenium
from webdriver import DesiredCapabilities
import re

to_cities = ['toulouse', 'bordeaux', 'marseille']
from_cities = [
                'paris',
                'toulouse',
                'bordeaux',
                'nimes',
                'montpellier',
                'lille',
                'lyon',
                'nice',
                'toulon',
                'marseille',
                'sophia'
                ]
source_url = 'http://www.autoroutes.fr/fr/itineraires.htm?itiFrom=%s&itiTo=%s'
desired_capabilities = dict( platform = "WINDOWS",
                                    browserName = "firefox",
                                    version = "3.6",
                                    name = "Get french highway car cost" )
driver = webdriver.Remote( desired_capabilities = desired_capabilities,
                          command_executor = 'http://YOUR_SAUCELABS_CREDENTIALS_HERE@ondemand.saucelabs.com:80/wd/hub' )
#the duration and cost load via ajax so add a timer to permit the datas to load
driver.implicitly_wait( 30 )
for city in from_cities :
    for destination in to_cities :
        if destination != city :
            completed_url = source_url % ( city, destination )
            driver.get( completed_url )
            price = driver.find_element_by_xpath( "//div[@id='dSummaryMsg']/b[3]" )
            time = driver.find_element_by_xpath( "//div[@id='dSummaryMsg']/b[2]" )
            print( city
                   + " "
                   + destination
                   + " "
                   + re.search( '\d+\.\d+', price.text ).group( 0 )
                   + " "
                   + re.search( '\d+H\d+', time.text ).group( 0 )
                )

driver.quit()