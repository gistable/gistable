import requests
product="MOBE8AHAT4SFH3PJ"
url="https://affiliate-api.flipkart.net/affiliate/product/json?id="
url=url+product
headers = {'Fk-Affiliate-Id': 'affliate_id','Fk-Affiliate-Token':'YOUR token'}
r = requests.get(url, headers=headers)
print r.content
