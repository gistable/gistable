
# following Python packages needs to be installed 
# xlrd, xlsxrd, unidecode, MySQLdb

import xlrd
import xlsxrd
import MySQLdb as mdb
import re
import unidecode

login = {}

#specify your database server credentials#
login['host'] = 'localhost'
login['username'] = 'root'
login['password'] = 'MNixv10a'
login['database'] = 'odesk'



#excel sheet file path#########################
excel_file_path  = 'consulate-listings.xlsx'







def get_cursor(host, username, password, database):
    
    try:
        conn = mdb.connect(host,username,password,database)
        return conn,conn.cursor()
    except:
        print 'Database connection failed!'
        return None


def slugify(the_string):
    the_string = unidecode.unidecode(the_string).lower()
    return re.sub(r'\W+','-',the_string)

    

conn,cursor = get_cursor(**login)
conn.set_character_set('utf8')
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')




workbook = xlsxrd.open_workbook(excel_file_path)
worksheet = workbook.sheet_by_name('Sheet1')

nrows = worksheet.nrows


print nrows






for each in range(1,nrows):
    print '###############'
    print 'row '+ repr(each) + ' inserted'
    print '###############'
    name = worksheet.row(each)[0].value#consulate name
    company_type = "consulate" #fixed string
    license_fee_type = worksheet.row(each)[1].value# GMT Time
    license_fee = worksheet.row(each)[2].value# Visa Processing Times
    url1 = worksheet.row(each)[4].value #Embasy URL
    text = worksheet.row(each)[5].value#Embasy Overview
    
    text = unidecode.unidecode(text)
    text = mdb.escape_string(text)
    continuing_education = text

    address = mdb.escape_string(unidecode.unidecode(worksheet.row(each)[6].value))# Address1
    city = worksheet.row(each)[7].value# city
    country = worksheet.row(each)[8].value# country
    ## email and url
    email = worksheet.row(each)[9].value#contact email
    url2 = []
    if email.find('\n'):
        emails = email.split('\n')
        email = emails[0]
        url2 = emails[1:]
    url2 = ''.join(url2)
    
    ##
    ##phone and renewal_fee
    phone = worksheet.row(each)[10].value#contact telephone
    renewal_fee = []
    if phone.find('\n'):
        data = phone.split('\n')
        phone = data[0]
        renewal_fee = data[1:]
    renewal_fee = ''.join(renewal_fee)
    ##
    
    renewal_deadline = worksheet.row(each)[11].value#work hours
    speciality_type = worksheet.row(each)[12].value#best contact
    slug = slugify(name)
    type_of_control = worksheet.row(each)[13].value#issue packet 3
    packet_4= worksheet.row(each)[14].value#issue packet 4  
    facility_type = worksheet.row(each)[15].value#photo of embassy
  
    #date_added = timestamp from the database sever during SQL insert

    query = """insert into lists_company (name,company_type, license_fee_type, licensing_fee,
    url1, description, address, city, country, email,
    url2, phone, renewal_fee, renewal_deadline, specialty_type, slug,
    type_of_control, packet_4, facility_type ) values ("%s","%s","%s","%s","%s",'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',"%s","%s","%s")"""%(name, company_type, license_fee_type, license_fee,
                                                                       url1, continuing_education, address, city, country,
                                                                       email, url2, phone, renewal_fee, renewal_deadline,
                                                                       speciality_type, slug, type_of_control, packet_4,
                                                                       facility_type)

    #print query
    
    cursor.execute(query)
    conn.commit()
    
    
    
    







