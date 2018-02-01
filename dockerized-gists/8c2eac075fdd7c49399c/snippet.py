__author__ = 'zachj'

import requests
import json

merchantId = 'INSERT YOUR MERCHANT ID HERE'
token = 'INSERT YOUR API TOKEN HERE'
apiToken = '?access_token=' + token
baseURL = 'https://api.clover.com/v3/merchants/' + merchantId + '/'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def printGetUrl(url):
    print bcolors.HEADER, "GET", bcolors.ENDC, url,

def printPostUrl(url):
    print bcolors.HEADER, "POST", bcolors.ENDC, url,

def printOk():
    print bcolors.OKGREEN, "Ok!", bcolors.ENDC

def printFailure(r):
    extra = ""
    if (r != None):
        extra = r
    print bcolors.FAIL, "** FAILED **", extra

def createOrder():
    url = baseURL + 'orders' + apiToken

    r = requests.post(url, headers=headers)
    if r.status_code == 200:
        printOk()
        return r.json()
    else:
        printFailure(r)

def getItems():
    url = baseURL + 'items' + apiToken
    r = requests.get(url)

    if r.status_code == 200:
        printOk()
        return r.json()
    else:
        printFailure(r)

def openOrder(order):
    url = baseURL + 'orders/' + order['id'] + apiToken

    data = {'state': 'open'}

    r = requests.post(url, data=json.dumps(data), headers=headers)

    if r.status_code == 200:
        printOk()
        return r.json()
    else:
        printFailure(r)

def getOrder(order):
    url = baseURL + 'orders/' + order['id'] + '?expand=lineItems&access_token='+token
    r = requests.get(url)
    if r.status_code == 200:
        printOk()
        return r.json()
    else:
        printFailure(r)

def addLineItem(order, item):
    url = 'https://api.clover.com/v3/merchants/'+merchantId+'/orders/'+order['id']+'/line_items'+apiToken
    # Pass the reference to the base item
    data = {'item': {'id': item['id']}}

    # If its variable price then set it to 50 for this demo
    if item['priceType'] == 'VARIABLE':
        data['price'] = 50

    # If its per unit then by 4 (so that 4000 because we allow 3 dec places)
    if item['priceType'] == 'PER_UNIT':
        data['unitQty'] = 4000

    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        printOk()
        print "\n" + item['name'].title() + " added to your order!\n"
        return r.json()
    else:
        printFailure(r)

def main():

    # Fetch inventory items
    items = getItems()

    # Create order and grab order ID
    order = createOrder()

    itemList = {}
    itemString = ""

    # Create a hashmap of {name -> id}, and create a string of item names
    for item in items['elements']:
        itemList[str(item['name']).lower()] = item['id']
        itemString += item['name'] + "\n"

    # Let the user shop for items
    while True:
        print "Enter an item to purchase, or type \"finish\" to complete the order:\n"
        print itemString
        option = raw_input().lower()
        if option == "finish":
            break
        elif option in itemList:
            itemID = itemList.get(option)
            myItem = requests.get(baseURL + 'items/' + itemID + apiToken).json()
            addLineItem(order, myItem)
        else:
            print("\nNot a valid item, please try again.\n")

    # Open the order so its visible on other devices
    openOrder(order)

    # Prints out the receipt address
    print "Order Complete!\nSee the receipt at - :" + 'https://clover.com/r/' + order['id']

    order = getOrder(order)
    print order

    print "When you arrive at our location, your order will be available for pickup.\nThank You!"

if __name__ == "__main__":
    main()