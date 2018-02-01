
###Imported Required Libraries
import requests, bs4
import webbrowser
import sqlalchemy
import unicodedata
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String
import mysql.connector
from mysql.connector import Error

engine = create_engine('mysql://username:<password>@<host>/<dbname>')

###Scraping Data From Booking.com
head = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}

url = "http://www.booking.com/searchresults.en-gb.html?dcid=4&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaGyIAQGYAS64AQjIAQzYAQHoAQH4AQuoAgM&lang=en-gb&sid=c24fad210186ae699e89a0d3cab10039&sb=1&src=index&src_elem=sb&error_url=http%3A%2F%2Fwww.booking.com%2Findex.en-gb.html%3Flabel%3Dgen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaGyIAQGYAS64AQjIAQzYAQHoAQH4AQuoAgM%3Bsid%3Dc24fad210186ae699e89a0d3cab10039%3Bdcid%3D4%3Bsb_price_type%3Dtotal%26%3B&prefill_submitted=1&ss=Kolkata%2C+India&ssne=Kolkata%2C+India&ssne_untouched=Kolkata%2C+India&dest_id=-2092511&dest_type=city&checkin_monthday=30&checkin_year_month=2016-6&checkout_monthday=1&checkout_year_month=2016-7&sb_travel_purpose=leisure&room1=A%2CA&no_rooms=1&group_adults=2&group_children=0"

res = requests.get(url, headers=head)

soup = BeautifulSoup(res.text,"html.parser")

hotels = soup.select("#hotellist_inner div.sr_item.sr_item_new")
details = []
for hotel in hotels:
     name = hotel.select("span.sr-hotel__name")
     score = hotel.select("span.average.js--hp-scorecard-scoreval")
     price = hotel.select("table div.sr-prc--num.sr-prc--final")
     for i in range(0,len(name)):
         #print name[i]
         #print type(name[i].getText().encode("ascii", "ignore"))
         details.append(name[i].getText().encode("ascii", "ignore"))
         #print score[i].getText()
         details.append(score[i].getText().encode("ascii", "ignore"))
     for i in range(0,len(price)):
         #print price[i].getText()
         details.append(price[i].getText().encode("ascii", "ignore"))
for j in range(0,len(details)):         
         print details[j]
###Initiating MySQL DB COnnection on Local Machine
def connect():
    try:
        conn = mysql.connector.connect(host='localhost',
        database='python_mysql',
        user='root',
        password='secret')
        if conn.is_connected():
            print('Connected to MySQL database')
    
    except Error as e:
        print(e)
    
    finally:
        conn.close()
    if name == 'main':
        connect()

###Creating Table on Local Machine

hotel_table = Table('Hotels', metadata,
Column('Hotelname', String),
Column('Hotelrating', String),)


metadata.create_all()

ins = hotel_table.insert()
for i in range(0,10):
    name[i].encode('ascii','ignore')
    rating[i].encode('ascii','ignore')

params = [(name[i], rating[i]) for i in range(10)]

###Inserting Data into MySQL Table 
def insert_hotels(params):
    query = "INSERT INTO hotel_table(hotel_name,hotel_rating) VALUES(%s,%s)"

try:
    db_config = read_db_config()
    conn = MySQLConnection(**db_config)

    cursor = conn.cursor()
    cursor.executemany(query, params)

    conn.commit()
except Error as e:
    print('Error:', e)

finally:
    cursor.close()
    conn.close()
def main():
    insert_hotels(params)

if name == 'main':
    main()