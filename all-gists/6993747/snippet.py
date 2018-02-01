import ebaysdk
from ebaysdk import finding

api = finding(siteid='EBAY-GB', appid='<REPLACE WITH YOUR OWN APPID>')

api.execute('findItemsAdvanced', {
    'keywords': 'laptop',
    'categoryId' : ['177', '111422'],
    'itemFilter': [
        {'name': 'Condition', 'value': 'Used'},
        {'name': 'MinPrice', 'value': '200', 'paramName': 'Currency', 'paramValue': 'GBP'},
        {'name': 'MaxPrice', 'value': '400', 'paramName': 'Currency', 'paramValue': 'GBP'}
    ],
    'paginationInput': {
        'entriesPerPage': '25',
        'pageNumber': '1' 	 
    },
    'sortOrder': 'CurrentPriceHighest'
})

dictstr = api.response_dict()

for item in dictstr['searchResult']['item']:
    print "ItemID: %s" % item['itemId'].value
    print "Title: %s" % item['title'].value
    print "CategoryID: %s" % item['primaryCategory']['categoryId'].value