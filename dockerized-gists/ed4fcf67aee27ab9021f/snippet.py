# -*- coding: utf-8 -*-
import requests
import json
import time
from decimal import *

token = 'place your Web API token here' # https://api.slack.com
api_url = 'https://slack.com/api/chat.postMessage'
data = {
'token': token,
'channel': '@blizzardblue',
'text': '모닝모닝',
'username': 'BlizzardBlue'
}

# 목표 시간
target_time = Decimal(time.mktime(time.strptime('2016-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')))

# 테스트 메시지 전송하여 레이턴시 리턴
def time_correction(api_url, data):
    request_time = Decimal(time.time())
    response = requests.post(api_url, data)
    response_time = Decimal(response.json()['ts'])
    print "request_time: {}\nresponse_time: {}\ndelta: {}\n".format(request_time, response_time, response_time - request_time)
    return response_time - request_time

# 테스트 10회 수행하여 레이턴시 평균 계산
time_correction_list = []
for i in range(10):
    time_correction_list.append(time_correction(api_url, data))
    time.sleep(2)

delta_mean = Decimal(0)
for t in time_correction_list:
    delta_mean += t

delta_mean = delta_mean / len(time_correction_list)

# 레이턴시 보정된 목표 시간
target_time_corrected = target_time - delta_mean

print "target time: {}\ntarget time corrected: {}".format(target_time, target_time_corrected)

# 보정된 목표 시간까지 루프
while True:
    if str(time.time()) == str(target_time_corrected)[:14]:
        response = requests.post(api_url, data = {
            'token': token,
            'channel': '#_general',
            'text': '모닝모닝',
            'username': 'BlizzardBlue'
            })

        print "DONE: {}".format(response.json()['ts'])
        exit(0)