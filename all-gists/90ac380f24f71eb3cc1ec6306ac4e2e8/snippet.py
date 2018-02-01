# Install the Python Requests library:
# `pip install requests`

import requests
import datetime
import pickle
set_date = datetime.datetime

# Simply call get_record and it will return a json object containing your bill.

# Replace them with your credentials. You can get all these credentials by capturing packets from WeChat app when viewing your bill. Hint: Surge.app can be very helpful.

exportkey = "xxxxxx"
cookie = "export_key=xxxxx; userroll_pass_ticket=xxxxxx"

def get_record(date,count):
    # https://wx.tenpay.com/userroll/userrolllist
    # GET https://wx.tenpay.com/userroll/userrolllist
    timestamp = date.timestamp()
    global exportkey, cookie
    if count > 200: # Cannot be greater than 200 per query.
        count = 200
    try:
        response = requests.get(
            url="https://wx.tenpay.com/userroll/userrolllist",
            params={
                "exportkey": exportkey,
                "count": str(count),
                "sort_type": "1",
                "start_time": str(timestamp),
                # "classify_type": "3", 3 is 面对面收钱， 2 is 红包
            },
            headers={
                "Cookie": cookie,
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Referer": "https://wx.tenpay.com/",
                "Accept-Encoding": "gzip, deflate",
                "Host": "wx.tenpay.com",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Mobile/14C92 MicroMessenger/6.5.3 NetType/WIFI Language/en",
                "Accept-Language": "en-us",
            },
        )
        print('Grabbed: {request_date}'.format(
            request_date=date.strftime("%B %d, %Y")))
        return response.json()
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
def save_pkl(target_object, filename="wechat_record.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(target_object, file)
        
def get_all_record(start, end, count=200, tries=5):
    # Assuming you won't have a daily bill of more than 200 transcations.
    current = start
    records = []
    pool = []
    error_date = []
    while current < end:
        attempts = 0
        done = False
        while attempts < tries:
            try:
                records += get_record(current, count)["record"]
                done = True
                break
            except:
                attempts += 1
        if not done:
            error_date.append(current)
        current += datetime.timedelta(days=1)
    pool = []
    offset = 0
    for i in range(len(records)):
        pointer = i - offset
        if records[pointer]["trans_id"] not in pool:
            pool.append(records[pointer]["trans_id"])
        else:
            records.pop(pointer)
            offset += 1
    return records, error_date

def get_all_record_inplace(start, end, count=200, tries=5):
    # This function is introduced in case you need to interrupt the operation without losing grabbed data.
    # Assuming you won't have a daily bill of more than 200 transcations.
    current = start
    global records # You need an empty list "records" to store the data.
    pool = []
    error_date = []
    while current < end:
        attempts = 0
        done = False
        while attempts < tries:
            try:
                records += get_record(current, count)["record"]
                done = True
                break
            except:
                attempts += 1
        if not done:
            error_date.append(current)
        current += datetime.timedelta(days=1)
    pool = []
    offset = 0
    for i in range(len(records)):
        pointer = i - offset
        if records[pointer]["trans_id"] not in pool:
            pool.append(records[pointer]["trans_id"])
        else:
            records.pop(pointer)
            offset += 1
    return error_date