from collections import defaultdict
import datetime
import requests
import time

CHECKINS_API = 'https://api.foursquare.com/v2/users/self/checkins'
CATEGORIES_API = 'https://api.foursquare.com/v2/venues/categories'
YEAR_BEGIN = int(time.mktime(datetime.date(2013,1,1).timetuple()))
YEAR_END = int(time.mktime(datetime.date(2014,1,1).timetuple()))
WEEK = int(time.mktime(datetime.date(2013,12,29).timetuple()))

PARAMS = {
    'oauth_token': 'TOKEN_HERE',
    'v': '20140104',
}

SUBCATEGORIES = {}
MAIN_CATEGORIES = []

def add_subcategory(main, cat):
    SUBCATEGORIES[cat['name'].encode('utf-8')] = main
    if cat.get('categories', False):
        for subcat in cat['categories']:
            add_subcategory(main, subcat)

response = requests.get(CATEGORIES_API, params=PARAMS).json()
for cat in response['response']['categories']:
    name = cat['name'].encode('utf-8')
    SUBCATEGORIES[name] = name
    MAIN_CATEGORIES.append(name)
    add_subcategory(name, cat)

print 'Processed categories'

PARAMS.update({
    'afterTimestamp': YEAR_BEGIN,
    'beforeTimestamp': YEAR_END,
    'limit': '250',
})

response = requests.get(CHECKINS_API, params=PARAMS).json()
print response['response']['checkins']['count'], 'checkins found'

count = 0
categories = defaultdict(int)
venues = defaultdict(int)
category_over_time = defaultdict(lambda: defaultdict(int))

with open('fsq_dump.csv', 'w') as output, open('fsq_category.csv', 'w') as category_output, open('fsq_venue.csv', 'w') as venue_output, open('fsq_category_over_time.csv', 'w') as category_over_time_output:
    while response['response']['checkins']['items']:
        for item in response['response']['checkins']['items']:
            if item['type'] != 'checkin':
                continue
                
            category = item['venue']['categories'][0]['name'].encode('utf-8')
            venue = item['venue']['name'].encode('utf-8')
            last = item['createdAt']
            
            categories[category] += 1
            venues[venue] += 1
            
            if int(last) < WEEK:
                WEEK -= 60*60*24*7
            category_over_time[WEEK][SUBCATEGORIES[category]] += 1
            
            output.write('{},{},{}\n'.format(item['createdAt'], venue, category))
            
            count += 1
            if count % 50 == 0:
                print count, 'processed'
            
        PARAMS['beforeTimestamp'] = last
        response = requests.get(CHECKINS_API, params=PARAMS).json()
    
    [category_output.write('{},{}\n'.format(*c)) for c in sorted(categories.iteritems(), key=lambda x: x[1], reverse=True)]
    [venue_output.write('{},{}\n'.format(*c)) for c in sorted(venues.iteritems(), key=lambda x: x[1], reverse=True)]
    
    sorted_categories_only = sorted(categories.iteritems(), key=lambda x: x[1], reverse=True)
    category_over_time_output.write('Week,{}\n'.format(','.join(MAIN_CATEGORIES)))
    [category_over_time_output.write('{},{}\n'.format(w, ','.join([str(category_over_time[w][c]) for c in MAIN_CATEGORIES]))) for w in sorted(category_over_time)]
    
    print 'Done'
    
