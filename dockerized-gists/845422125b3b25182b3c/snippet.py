#Author: Arockia
"""Use this script to monitor the price of products from Amazon and get alert when there is a fall in price."""


import urllib, requests, codecs, datetime, os,smtplib
from email.mime.text import MIMEText

import BeautifulSoup

filename="ProductPriceHistory.txt"

products_url=[
    "http://www.amazon.in/OnePlus-One-Sandstone-Black-64GB/dp/B00OK2ZW5W/ref=sr_1_1?ie=UTF8&qid=1456825859&sr=8-1&keywords=oneplus+one",
    "http://www.amazon.in/OnePlus-E1003-X-Onyx-16GB/dp/B016UPKCGU/ref=sr_1_2?ie=UTF8&qid=1456825859&sr=8-2&keywords=oneplus+one",
    "http://www.amazon.in/Sony-16GB-Microvault-Flash-Drive/dp/B0073C7IIK/ref=lp_1375411031_1_2?s=computers&ie=UTF8&qid=1456901501&sr=1-2",
    "http://www.amazon.in/Apple-Macbook-MD101HN-Mavericks-Graphics/dp/B00DKMCB20/ref=sr_1_1?s=computers&ie=UTF8&qid=1457004660&sr=1-1&keywords=laptop",
    "http://www.amazon.in/Apple-MacBook-MJVE2HN-13-inch-Yosemite/dp/B00VBHQU78/ref=sr_1_23?s=computers&ie=UTF8&qid=1457005164&sr=1-23&keywords=laptop",
    "http://www.amazon.in/Dell-Premium-Built-14-1-Inch-Professional-Refurbished/dp/B00VKL0I96/ref=sr_1_24?s=computers&ie=UTF8&qid=1457005164&sr=1-24&keywords=laptop"
    ]

def get_prod_info(url):
    resp = requests.get(url,proxies=urllib.getproxies())
    soup = BeautifulSoup.BeautifulSoup(resp.text,fromEncoding='utf-8')
    prod_info = {'name':'','price':''}

    prod_column=soup.find(attrs={'id':'centerCol'})
    p_name = prod_column.find(attrs={'id':'productTitle'})
    p_our_price = prod_column.find(attrs={'id':'priceblock_ourprice'})
    p_sale_price = prod_column.find(attrs={'id':'priceblock_saleprice'})
    p_deal_price = prod_column.find(attrs={'id':'priceblock_dealprice'})
    p_misc_price =prod_column.find(attrs={'class':'a-color-price'})

    if p_name:
        prod_info['name'] = p_name.text
        if p_our_price:
            prod_info['price'] = p_our_price.text
        elif p_sale_price:
            prod_info['price'] = p_sale_price.text
        elif p_deal_price:
            prod_info['price'] = p_deal_price.text
        else:
            prod_info['price'] = p_misc_price.text

    return prod_info

def print_all_data(filename,mode='r'):
    print "Reading Data..."
    f = open(filename,mode=mode)
    content = f.readlines()[0].split("***")
    for entry in content:
        for item in entry.split('##'):
            if len(item.split("#")) == 3:
                print "Date: " + item.split("#")[0]
                print "Name: " + item.split("#")[1]
                print "Price: Rs " + item.split("#")[2]

def compare_latest_price(mode='r'):
    print "Checking with previous price"
    f = open(filename,mode=mode)
    content = f.readlines()[0].split("***")
    f.close()
    alert_list=[]
    if len(content) > 2:
	    previous_line = content[-3].split('##')
	    current_line = content[-2].split('##')
	    i=0
	    if len(previous_line) > 0 and len(current_line) >0:
		    while i<len(previous_line)-1:
			if float(current_line[i].split('#')[2]) < float(previous_line[i].split('#')[2]):
			    print "Hurry Up... Price is Low..." + current_line[i]
			    alert_list.insert(len(alert_list)+1,current_line[i])
			i=i+1
    print "Checks done..."
    return alert_list

def update_data():
    print "Updating Current Price "
    products_info = []
    for url in products_url:
        products_info.insert(len(products_info)+1,get_prod_info(url))

    f = codecs.open(filename,mode='a',encoding='utf-8')
    format = "%d-%m-%Y %H:%M:%S"
    today=datetime.datetime.today()

    if len(products_info):
        for prod in products_info:
            result = str(today.strftime(format)) + "#" + prod['name'] + "#" + unicode(prod['price']).replace(',','').replace('&nbsp;','').strip()
            f.writelines(result+"##")
        f.writelines("***")
        f.close()

def send_mail(content):
   print "Sending Alert Mail"
   server = smtplib.SMTP('smtp.gmail.com',587)
   server.starttls()
   from_addr = 'user1@gmail.com'
   to_addr = 'user2@gmail.com'
   content_txt=""
   for line in content:
   	content_list=line.split("#")
	content_txt = content_txt + "Price got dropped for " + content_list[1] + ". Now available at Rs. " + content_list[2] +". Price updated by " + content_list[0]
   content_txt = content_txt + ". Thank You..."	
   msg = MIMEText(content_txt)
   msg['To'] = from_addr
   msg['From'] = to_addr
   msg['Subject'] = 'Product Price Alert'
   server.login('sender_address@gmail.com','Password')
   server.sendmail(from_addr,to_addr,msg)
   server.quit()

if __name__ == "__main__":
    update_data()
    print_all_data(filename=filename,mode='r')
    alert_list = compare_latest_price()
    if len(alert_list) > 0:
        send_mail(content=alert_list)