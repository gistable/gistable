#!/usr/bin/env python
from re import findall,sub
from lxml import html
from time import sleep
from selenium import webdriver
from pprint import pprint
from xvfbwrapper import Xvfb

def parse(url):
    searchKey = "Las Vegas" # Change this to your city 
    checkInDate = '27/08/2016' #Format %d/%m/%Y
    checkOutDate = '29/08/2016' #Format %d/%m/%Y
    response = webdriver.Firefox()
    response.get(url)
    searchKeyElement = response.find_elements_by_xpath('//input[contains(@id,"destination")]')
    checkInElement = response.find_elements_by_xpath('//input[contains(@class,"check-in")]')
    checkOutElement = response.find_elements_by_xpath('//input[contains(@class,"check-out")]')
    submitButton = response.find_elements_by_xpath('//button[@type="submit"]')
    if searchKeyElement and checkInElement and checkOutElement:
        searchKeyElement[0].send_keys(searchKey)
        checkInElement[0].clear()
        checkInElement[0].send_keys(checkInDate)
        checkOutElement[0].clear()
        checkOutElement[0].send_keys(checkOutDate)
        randomClick = response.find_elements_by_xpath('//h1')
        if randomClick:
            randomClick[0].click()
        submitButton[0].click()
        sleep(15)
        dropDownButton = response.find_elements_by_xpath('//fieldset[contains(@id,"dropdown")]')
        if dropDownButton:
            dropDownButton[0].click()
            priceLowtoHigh = response.find_elements_by_xpath('//li[contains(text(),"low to high")]')
            if priceLowtoHigh:
                priceLowtoHigh[0].click()
                sleep(10)

    parser = html.fromstring(response.page_source,response.current_url)
    hotels = parser.xpath('//div[@class="hotel-wrap"]')
    for hotel in hotels[:5]: #Replace 5 with 1 to just get the cheapest hotel
        hotelName = hotel.xpath('.//h3/a')
        hotelName = hotelName[0].text_content() if hotelName else None
        price = hotel.xpath('.//div[@class="price"]/a//ins')
        price = price[0].text_content().replace(",","").strip() if price else None
        if price==None:
            price = hotel.xpath('.//div[@class="price"]/a')
            price = price[0].text_content().replace(",","").strip() if price else None
        price = findall('([\d\.]+)',price) if price else None
        price = price[0] if price else None
        rating = hotel.xpath('.//div[@class="star-rating"]/span/@data-star-rating')
        rating = rating[0] if rating else None
        address = hotel.xpath('.//span[contains(@class,"locality")]')
        address = "".join([x.text_content() for x in address]) if address else None
        locality = hotel.xpath('.//span[contains(@class,"locality")]')
        locality = locality[0].text_content().replace(",","").strip() if locality else None
        region = hotel.xpath('.//span[contains(@class,"locality")]')
        region = region[0].text_content().replace(",","").strip() if region else None
        postalCode = hotel.xpath('.//span[contains(@class,"postal-code")]')
        postalCode = postalCode[0].text_content().replace(",","").strip() if postalCode else None
        countryName = hotel.xpath('.//span[contains(@class,"country-name")]')
        countryName = countryName[0].text_content().replace(",","").strip() if countryName else None

        item = {
                    "hotelName":hotelName,
                    "price":price,
                    "rating":rating,
                    "address":address,
                    "locality":locality,
                    "region":region,
                    "postalCode":postalCode,
                    "countryName":countryName,
        }
        pprint(item)
if __name__ == '__main__':
    vdisplay = Xvfb()
    vdisplay.start()
    parse('http://www.hotels.com')
    vdisplay.stop()
