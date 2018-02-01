# log from ipython as I played with the pricing api
#index.json from https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json
# Per http://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html#download-the-offer-index
# But this may no longer be supported as it (EC2) is not part of the parent index of all services any longer

import json
with open('index.json', 'r') as foo:
    data = json.read(foo)

with open('index.json', 'r') as foo:
    data = json.load(foo)

data.keys()
for key in data:
    print(data[key])

data.keys()
for key in data:
    if key != 'products':
        print(data[key])

data.keys()
for key in data:
    print(key)

for key in data:
    if key != u'products':
        print(data[key])

for key in data:
    if key != u'products':
        print('{} {}'.format(key, len(data[key])))

data['offerCode']
data['terms']
print(data['terms'])
for key in data:
    if key != 'terms':
        print(data[key])

for key in data:
    if key != u'products':
        print('{} {}'.format(key, len(data[key])))

print(data['products'])
print(data['terms'])
print(data.keys())
for key in data:
    if key != u'products' and key != 'terms':
        print('{} {}'.format(key, len(data[key])))

for key in data:
    if key != u'products' and key != 'terms':
        print(data[key])

for key in data:
    if key != u'products' and key != 'terms':
        print(key, data[key])

for foo in data['terms']:
    print(foo)
    break

type(data['terms'])
data['terms'].keys()
type(data['terms']['OnDemand'])
data['terms']['OnDemand'].keys()
data['terms']['OnDemand']['G4GEXKDQYPCVBPS5']
len(data['terms']['OnDemand'].keys())
len(data['products'].keys())
del(data['terms'])
data['products'].keys()
data['products']['24GRA8RB2KZ9NPCS']
[product for product in data['products'] if product['attributes']['tenacy'] == 'Shared']
[product for product in data['products']]
[data[product] for product in data['products'] if data[product]['attributes']['tenacy'] == 'Shared']
[data[product] for product in data['products'] if data['products'][product]['attributes']['tenacy'] == 'Shared']
[data[product] for product in data['products'] if data['products'][product]['attributes']['tenancy'] == 'Shared']
[data['products'][product] for product in data['products'] if data['products'][product]['attributes']['tenancy'] == 'Shared']
data['products']['8PYMHJ67798U4J44']
[data['products'][product] for product in data['products'] if data['products'][product]['attributes'].get('tenancy') == 'Shared']
len([data['products'][product] for product in data['products'] if data['products'][product]['attributes'].get('tenancy') == 'Shared'])
products = [data['products'][product] for product in data['products'] if data['products'][product]['attributes'].get('tenancy') == 'Shared']
del data
products
len(products)
products[-1]
products['UHFGRAHKZHCM4KKD']
with open('index.json', 'r') as foo:
    data = json.load(foo)

data['products']['UHFGRAHKZHCM4KKD']
del(data['terms'])
del data
dir(products)
products
products[0]
[product for product in products if product['attributes']['instanceType'].startswith('x1')]
len([product for product in products if product['attributes']['instanceType'].startswith('x1')])
len([product for product in products if product['attributes']['location'] == 'EU (Ireland)'])
len([product for product in products if product['attributes']['instanceType'].startswith('x1') and product['attributes']['location'] == 'EU (Ireland)'])
[product for product in products if product['attributes']['instanceType'].startswith('x1') and product['attributes']['location'] == 'EU (Ireland)']
[product for product in products if product['attributes']['instanceType'].startswith('x1') and product['attributes']['location'] == 'EU (Ireland)' and product['attributes']['operatingSystem'] == 'Linux']
[product for product in products if product['attributes']['instanceType'].startswith('x1.16') and product['attributes']['operatingSystem'] == 'Linux']
with open('index.json', 'r') as foo:
    data = json.load(foo)

data['terms']['F3VADBY3Z6MMHKTQ']
data['terms'].keys()
data['terms']['Reserved']['F3VADBY3Z6MMHKTQ']
