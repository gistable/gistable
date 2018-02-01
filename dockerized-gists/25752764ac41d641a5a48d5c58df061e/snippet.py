#!/usr/bin/env python

"""
    author: sidd607@gmail.com
    version: 0.0.1

    Reads the buy details from a csv file (coins.csv) and calculates the wallets profit
    Uses Koinex API tracker
    csv format
    Coin,Date,Quantity,BuyPrice,Cost

    Coin - Coin symbol BTC etc.
    Date - Date at which bought
    Quantity - Number of coins bought
    BuyPrice - Price at which the coins were bought
    Cost - Total cost = Quantity * BuyPrice

"""
import sys
import subprocess as sp
import getopt
import requests
import csv
import time
from datetime import datetime
import os

coin_sym = {
    "BTC" : "Bitcoin",
    "ETH" : "Ether",
}

class PriceTracker:

    def __init__(self):
        self.price = {}
        self.price_list = {}
        self.profit_list = {}
        self.koinex_details = {}

    def get_current_price(self):
        reply = requests.get('https://koinex.in/api/ticker')
        if reply.status_code != 200:
            raise Exception("Cannot connect to Koinex Ticker API - Check internet connection")
        else:
            self.koinex_details = reply.json()['stats']
            self.price = reply.json()['prices']
            for key in self.price:
                self.price_list[key] = []
                

    def get_user_data(self):
        f = open('coins.csv')
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            self.price_list[row['Coin']].append(row)



    def calculate_profit(self):
        for key in self.price_list:
            if self.price_list[key]:
                profit = 0
                value = 0
                coins = 0
                for tmp in self.price_list[key]:
                    profit += (float(self.price[key]) - float(tmp['BuyPrice'])) * float(tmp['Quantity'])
                    value += float(tmp['Quantity']) * float(self.price[key])
                    coins += float(tmp['Quantity'])

                self.profit_list[key] = (profit, value, coins)

    def print_data(self, details):
        total_profit = 0
        total_value = 0
        for key in self.profit_list:
            total_profit += self.profit_list[key][0]
            total_value += self.profit_list[key][1]
        print ""
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print "Value: " + str(total_value) + " | Profit: " + str(total_profit)
        print ""

        for key in self.profit_list:
            
            print key
            print "Current Price: " + str(self.price[key]),
            print  " | Value: " + str(self.profit_list[key][1]),
            print " | Profit: " + str(self.profit_list[key][0]),
            print " | Highest Bid: " + self.koinex_details[key]['highest_bid'],
            print " | Sell All: " + str( self.profit_list[key][2] * float(self.koinex_details[key]['highest_bid'])   )

            if details:
                total_amount = 0
                for i in self.price_list[key]:
                    total_amount += float(i['Cost'])
                print "Total amount spent: " + str(total_amount) + " | Profit Ratio: " + str((self.profit_list[key][0] / total_amount)),
                print " | ROI: " +  str(self.profit_list[key][2] * float(self.koinex_details[key]['highest_bid']) - total_amount)
                for i in self.price_list[key]:
                    print "--- Date: " + i['Date']  + " | Quantity: " + i['Quantity'] + " | Buy Price: " + i['BuyPrice'] + " | Cost: " + i['Cost'],
                    print " | Profit:" + str((float(self.price[key]) - float(i['BuyPrice']))* float(i['Quantity']))
                
            print ""
    
        if details:
            pass


    def print_price(self):
        print "Koinex prices as of " +  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for key in self.price:
            print key,
            print " \t ",
            print self.price[key]

def main(argv):
    getDetails = False
    loop = False
    delay = 0
    onlyPrice = False
    try:
        opts, args = getopt.getopt(argv, "hvl:p")
    except getopt.GetoptError:
        print "add -v for detailed report"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print "python main.py -v (for verbose output) -l (refresh every 10 seconds) -p (Display only prices at Koinex)"
            sys.exit()
        elif opt =="-v":
            getDetails = True
        elif opt == "-l":
            loop  = True
            delay = int(arg)
        elif opt == "-p":
            onlyPrice = True
    if loop:
        tmp = sp.call('clear',shell=True)
    
    
    while True:
        priceTracker = PriceTracker()
        priceTracker.get_current_price()
        if onlyPrice:
            priceTracker.print_price()
        else:
            priceTracker.get_user_data()
            priceTracker.calculate_profit()
        
            tmp = sp.call('clear',shell=True)
            priceTracker.print_data(getDetails)
        
        if not loop:
            break
        else:
            time.sleep(10)
            

if __name__ == '__main__':
    main(sys.argv[1:])