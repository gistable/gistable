#!/usr/bin/env python
import csv
import time
import cx_Oracle

# Parses USPS addresses from voter addresses
# and inserts them into VR_LOCATION table ready
# for geocoding. Does batches by zipcode
def LoadZips():
    zipcodes = []
    zips = open('OH_ZIP_CODES.txt','r')
    for line in zips:
        zip = line[0:5]
        if zip not in zipcodes:
            zipcodes.append(zip)
    zips.close()
    return zipcodes

def UpdateAddresses(ziplist):
    counter = 1
    total = len(ziplist)
    
    for zipcode in ziplist:
        orcl = cx_Oracle.connect('voter/voter@oracle')
        curs = orcl.cursor()
        countsql = "select count(*) from vr_location where zip_co = '%s'" % zipcode
        concatsql = """update vr_location l set l.usps_address=(
                        select mizar.string_utils.remove_duplicate_whitespace(
                            house_number
                            ||' '||pre_street_direction
                            ||' '||street_name
                            ||' '||street_description
                            ||' '||post_street_direction)
                        from vr_address a where a.address_pk = l.address_pk)
                    where zip_co = '%s'""" % zipcode
        parsesql = """update vr_location set usps_address = mizar.usaddress_utils.parse_address(usps_address)
                    where zip_co = '%s'""" % zipcode
        curs.execute(countsql)
        
        records_affected = curs.fetchone()[0]
        if records_affected == 0:
            print "No records for zipcode %s" % zipcode
            counter += 1 
            continue
        
        print "[%s] %s of %s: %s addresses" % (zipcode, counter, total, records_affected)
        curs.execute(concatsql)
        orcl.commit()
        curs.execute(parsesql)
        orcl.commit()
        curs.close()
        counter += 1 

        # Uncomment this to debug - just steps through X zipcodes      
        #if counter == 3:
        #    print &quot;Cleaning up...&quot;
        #    break
        

if __name__ == "__main__":
    start = time.clock()
    zipcodes = LoadZips()
    print "Processing addresses in %s zip codes" % len(zipcodes)
    UpdateAddresses(zipcodes)