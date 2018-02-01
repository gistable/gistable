from BeautifulSoup import BeautifulStoneSoup as bs
from quick_orm.core import Database
from sqlalchemy import Column,String,Text,Boolean
import bottlenose
import pprint
import logging
import re 
import time
import xlrd

#amazon keys 
AWS_KEY = "AKIAIPTBXUAPSQ3LNYEA"
SECRET_KEY = "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"
ASSOCIATE_TAG = "wwwgetgreacom-20"
    
#colored ouput :) thanks StackOverflow
#there is a better method to do this, but for now, this will do 
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30
#These are the sequences need to get colored ouput

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': GREEN,
    'INFO': BLUE,
    'DEBUG': GREEN,
    'CRITICAL': YELLOW,
    'ERROR': RED
    }

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):
    FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.WARNING)                

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return


logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger('amazon_scrape')
#sh = logging.StreamHandler()
#log_format = ColoredFormatter('[%(asctime)s][%(levelname)s]%(message)s')
#sh.setFormatter(log_format)
#sh.setLevel(logging.WARNING)
#logger.addHandler(sh)


#base Amazon API initialzation 
api = bottlenose.Amazon(AWS_KEY, SECRET_KEY, ASSOCIATE_TAG,"ItemLookup")
db = None #database handle 

#this is the DB table for Book Info
class BookInfo(object):
    __metaclass__ = Database.DefaultMeta

    #id 
    #id = Column(Integer, primary_key=True)
    #core info
    id  = Column(Text,primary_key=True ) #id is isbn
    isbn = Column(Text)
    title = Column(Text)
    price = Column(Text)
    authors = Column(Text)
    binding = Column(Text)
    mrp = Column(Text)
    sp = Column(Text)

    #extra info 
    number_of_pages  = Column(Text)
    publisher  = Column(Text)
    pub_date  = Column(Text)
    weight = Column(Text)
    isbn_13 = Column(Text)
    
    #large text 
    description = Column(Text) 
    categories = Column(Text)
   
    #image URLs 
    small_image = Column(Text)
    med_image = Column(Text)
    large_image = Column(Text)

    #hidden/refernce
    amazon_url = Column(Text)
    asin = Column(Text)
    similar_products = Column(Text)
    rank = Column(Text)

class ISBNList(object) :
    __metaclass__ = Database.DefaultMeta
    
    isbn = Column(String(20))
    downloaded = Column(Boolean)

#tor stuff

import socks 
import socket 

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1" , 8118 )
#we are setting the socket to the socks socket so that every connection
#goes throught TOR, Idea here is to change IP every 100 transactions ?
# see http://www.readtfb.net/2011/03/25/using-tor-with-python/
# see http://fscked.org/projects/torctl  tor homepage and
# http://stackoverflow.com/questions/2537726/using-urllib2-with-socks-proxy on the socks part
socket.socket = socks.socksocket
MAX_TRANSACTION=100

def tor_change_ip() :
    from TorCtl import TorCtl
    conn = TorCtl.connect(passphrase='1234')
    conn.sendAndRecv("signal newnym\r\n")
    conn.close()
    logger.warn("Changing IP address")
    time.sleep(5)
    
#tor end



def db_init():
    global db 
    #db = Database('sqlite:///amazon_data.db')
    db = Database('mysql://root:root@localhost/amazon_data?charset=utf8')
    db.create_tables()

def insert_in_db(data):
    db_entry = BookInfo( id = data['isbn'] ,  isbn = data['isbn'], title = data['title'], price = data['price'],
                        binding = data['binding'], number_of_pages = data['numberofpages'], isbn_13 = data['isbn_13'],
                        publisher = data['publisher'] , pub_date = data['publicationdate'],
                        weight = data['weight'] , description = data['content'] ,mrp=data['mrp'] , sp=data['sp'],
                        small_image = ''.join(data['smallimage']) , med_image = ''.join(data['mediumimage']) , large_image=''.join(data['largeimage']),
                        amazon_url = data['detailpageurl'] , asin = data['asin'] , rank = data['salesrank'],
                        authors = '####'.join(data['author']) ,  categories = '####'.join(data['browsenodes']),
                        similar_products = '####'.join(data['similarproducts']))

    db.session.add_then_commit(db_entry)
    

            
def get_book_info(isbn):
    #data extraction helpers 
    def get_string_from_xml( xml_root , key ) :
            if xml_root.find(key) :
                return { key : xml_root.find(key).text }
            
            return {key : '' }
    def get_list_from_xml( xml_root , key ) :
            if xml_root.find(key) :
                values = list()
                for v in xml_root.findAll(key) :
                    values.append(v.text)
                return { key : values } 
            return { key : '' }

    def get_children_list_from_xml(xml_root,parent,children) :
            xml_parent = xml_root.find(parent)
            if xml_parent and xml_parent.find(children) :
                values = list()
                for v in xml_parent.findAll(children) :
                    values.append(v.text)
                return { parent : values }
            return { parent : '' }
     
    amazon_data = dict()
    amazon_data['isbn_13'] = isbn # XXX: assumption here is that the isbn passed is always isbn-13
    single_value_keys = [  'Binding', 'NumberOfPages', 'Content', 'SalesRank',
                            'PublicationDate', 'Publisher' , 'Title', 
                            'Weight', 'ASIN', 'ISBN', 'DetailPageURL' ]

    list_value_keys = [ 'Author']

    parent_child_keys = [ ('SimilarProducts' , 'ASIN' ), ( 'SmallImage' , 'URL') , 
                          ( 'MediumImage' , 'URL') , ( 'LargeImage' , 'URL' ) ,
                          ( 'BrowseNodes' , 'Name') ]

    try :
        root = api.ItemLookup(ItemId=isbn, IdType="ISBN",SearchIndex="Books" ,  ResponseGroup="Large")
        soup = bs(root)
        if soup.find('error') :
            logger.error('Error from Amaazon: %s ' , soup.find('error').find('message').text)
            return None
         #other stuff

        for key in single_value_keys :
            amazon_data.update(get_string_from_xml(soup , key.lower() ))

        for key in list_value_keys : 
            amazon_data.update(get_list_from_xml(soup , key.lower() ))

        for parent,child in parent_child_keys : 
            amazon_data.update(get_children_list_from_xml(soup,parent.lower() , child.lower() ))

        #taking out price is a bit more involved 
        if  soup.find('condition' , text = re.compile('.*New.*')) :
            try : # I should'nt be doing this
                amazon_data['price'] = soup.find('condition',text=re.compile(r'.*New.*')).parent.parent.parent.find('formattedprice').text
            except : 
                amazon_data['price'] = ''
        return amazon_data
        #print soup.prettify()
            
    except Exception   as e:
        raise e
        logger.error("Got exception while fetching data")


#get_book_info('1597494860')
#get_book_info('159327288X')
db_init()
#get_book_info('0890068399')
#isbn_list = open('isbn_list.txt')    
wb = xlrd.open_workbook('books.xls')
sheet = wb.sheet_by_index(0)
#pp.pprint(dir(sheet))
rows = sheet.nrows
trans_count = 0  
for row in xrange(1,rows) :
    try:
        isbn = "%d" % sheet.cell(row,0).value
        mrp = "%0.2f" % sheet.cell(row,5).value
        sp = "%0.2f" % sheet.cell(row,6).value
        print "%d:%s mrp %s sp %s " % (row,isbn,mrp,sp)
        data = get_book_info(isbn)
        trans_count+=1
        if trans_count >= MAX_TRANSACTION :
            tor_change_ip()

        data['mrp'] = mrp
        data['sp'] = sp
    except Exception as e : 
        print "Got excpetion while fetching data" , e 

    if data :
        try :
           insert_in_db(data)
           logger.warning('Successfully inserted %s' % isbn)  
        except Exception as e:
            msg = "Got Error while inserting data to DB %s" %  e
            logger.error(msg + "\n" + '-' *30 + "\nData \n :" +  pprint.pformat(data))
            db.session.rollback()
    time.sleep(3)
