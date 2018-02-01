import xlrd
import cx_Oracle
import glob
import time
import os.path
import datetime

# _mtype = '/FTP/JKCS/*.xlsx'
_mtype = 'C:/Users/OchiengB/Desktop/freezie/*.xlsx'
time.strftime('%y-%b-%d %H:%M:%S')

_mcount = 0
for filename in glob.glob(_mtype):
    # fh = open(filename, 'r')

    list = xlrd.open_workbook(filename)
    worksheet = list.sheet_by_index(0)

    database = cx_Oracle.connect('warrantytracker', 'warranty#tracker', '10.2.2.50:1521/dwhdev')
    # database = cx_Oracle.connect('etl', 'etl', '10.2.2.35:1521/warehouse')
    cursor = database.cursor()

    for r in range(1, worksheet.nrows):
        AGENT_NAME = worksheet.cell(r, 0).value
        if str(worksheet.cell(r, 1)).split(':')[0] == 'xldate':
            a1 = worksheet.cell(r, 1).value
            a1_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(a1, list.datemode))
            TICKET_ISSUE_DATE =a1_as_datetime.strftime('%d-%b-%Y')
        else:
            dated = worksheet.cell(r, 1).value
            dated1 = datetime.datetime.strptime(dated, "%d-%b-%y %H:%M:%S")
            TICKET_ISSUE_DATE = dated1.strftime('%d-%b-%Y')
        PNR = worksheet.cell(r, 2).value
        ETICKET_NO = worksheet.cell(r, 3).value
        PASSENGER_NAME = worksheet.cell(r, 4).value
        PAYMENT_MODE = worksheet.cell(r, 5).value
        CURRENCY_CODE = worksheet.cell(r, 6).value
        FARE = worksheet.cell(r, 7).value
        TAX = worksheet.cell(r, 8).value
        FEE = worksheet.cell(r, 9).value
        FEE_1 = worksheet.cell(r, 10).value
        CREATED_BY = worksheet.cell(r, 11).value

        # print TICKET_ISSUE_DATE
        # print filename

        #TICKET_ISSUE_DATE = now.strftime('%y-%b-%d %H:%M:%S')




       # WARRANTYTRACKER.T_TICKET_ISSUED
        #ETL.T_TICKET_ISSUED
        query = """insert into WARRANTYTRACKER.T_TICKET_ISSUED (AGENT_NAME,TICKET_ISSUE_DATE,PNR,ETICKET_NO,PASSENGER_NAME,PAYMENT_MODE,CURRENCY_CODE,FARE,TAX,FEE,
           FEE_1,CREATED_BY)
             values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (
            AGENT_NAME, TICKET_ISSUE_DATE, PNR, ETICKET_NO, PASSENGER_NAME, PAYMENT_MODE, CURRENCY_CODE, FARE, TAX,
            FEE,FEE_1, CREATED_BY)
        # execute query
        cursor.execute(query)

        # Commit the transaction
        database.commit()
        # Close the cursor
        
    print("All done !")
    columns = str(worksheet.ncols)
    rows = str(worksheet.nrows)
    print ("i just import " + columns + " columns and " + rows + " rows ")

cursor.close()
    # Close the database connection
database.close()