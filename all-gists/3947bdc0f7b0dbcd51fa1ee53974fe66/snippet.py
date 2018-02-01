# coding=utf-8
import StringIO
import csv
import requests
from bs4 import BeautifulSoup
import time
import random
from Models import *


def fetch_stock_ids():
    try:
        response = requests.get(
            url="http://isin.twse.com.tw/isin/C_public.jsp",
            params={
                "strMode": "2",
            },
        )
        soup = BeautifulSoup(response.content, 'lxml')
        trs = soup.find_all('tr')[2::]
        ids = []
        for tr in trs:
            if len(tr.findChildren(['td'])) > 1:
                first_td_contents = tr.find('td').contents[0]
                the_id = first_td_contents[:4]
                ids.append(the_id)
            else:
                print('Fetched ' + str(len(ids)) + ' stock ids')
                return ids

    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def create_database():
    DB.connect()
    if not DailyTradeResult.table_exists():
        DB.create_table(DailyTradeResult)
    DB.close()


def date_from_string(string):
    array = string.split('/')
    return datetime.date(int(array[0]) + 1911, int(array[1]), int(array[2]))


def fetch_stock_track_results_in_month(year, month, stock_number):
    try:
        response = requests.post(
            url="http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAYMAIN.php",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            },
            data={
                "query_year": year,
                "CO_ID": stock_number,
                "query_month": month,
                "download": "csv",
            },
        )
        csv_string = StringIO.StringIO(response.content)
        reader = csv.reader(csv_string)
        rows = list(reader)[2::]
        if len(rows) == 1 and len(rows[0]) < 3:
            return
        return rows

    except requests.exceptions.RequestException:
        log_file = open('fetch_stock_failed.log', 'a')
        log_file.write('{}, {}, {}'.format(year, month, stock_number))
        log_file.close()


def save_records(record_in_month, stock_id_string):
    for record in record_in_month:
        if len(record) < 2:
            pass
        the_date = date_from_string(record[0])
        record = DailyTradeResult(stock_id=str(stock_id_string), date=the_date,
                                  unit_count=int(record[1].replace(',', '')),
                                  total_money=int(record[2].replace(',', '')),
                                  o_price=float(record[3].replace(',', '')),
                                  h_price=float(record[4].replace(',', '')),
                                  l_price=float(record[5].replace(',', '')),
                                  c_price=float(record[6].replace(',', '')),
                                  diff=str(record[7]), trade_count=int(record[8].replace(',', '')), )
        record.save()


def fetch_stock_price(stock_id_string):
    for year in range(DateHandler.THIS_YEAR, DateHandler.FIRST_YEAR - 1, -1):
        for month in range(12, 0, -1):
            local_stock = DailyTradeResult.select().where(
                DailyTradeResult.stock_id == str(stock_id_string)).order_by(DailyTradeResult.date)
            this_month = [x for x in local_stock if (x.date.year == year and x.date.month == month)]
            if len(this_month) == 0:
                print 'stock id: ' + stock_id_string + ', year month: ' + str(year) + ' ' + str(month)
                records_in_month = fetch_stock_track_results_in_month(year, month, str(stock_id_string))
                if records_in_month is not None:
                    save_records(records_in_month, stock_id_string)


if __name__ == '__main__':
    create_database()
    stock_ids = fetch_stock_ids()
    for stock_id in stock_ids:
      fetch_stock_price(stock_id)
            
