# coding: utf-8
import json
import re

import requests

# 替换成你自己的经纬度数据
# 查询方式 打开饿了么官网 -> 开发者模式 -> 输入送餐地址 -> 观察请求 -> 找到经纬度数据
latitude = 31.23978
longitude = 121.49968

url = "https://mainsite-restapi.ele.me/shopping/restaurants"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "offset": 0,
    "limit": 20,
    "extras[]": "activities",
    "restaurant_category_ids[]": 207,
    "support_ids[]": 8
}

headers = {
    "Host": "mainsite-restapi.ele.me",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
}

# 默认查询5页 共100家店
for i in range(5):
    print("Page %d:" % (i + 1))
    params["offset"] = i * params["limit"]
    data = json.loads(requests.get(url, params=params, headers=headers).text)
    for restaurant in data:
        id = restaurant["id"]
        name = restaurant["name"]
        for activity in restaurant["activities"]:
            if "type" in activity and activity["type"] == 102:  # 102 表示满减
                tips = activity["tips"]
                flag = True
                for couple in zip(* [iter(re.findall(r'\d+', tips))] * 2):
                    x = int(couple[0])
                    y = float(couple[1])
                    # 根据经验 只有所有折扣都是5折 才是真正的打折
                    if x / y != 2:
                        flag = False
                        break
                if flag:
                    print("\t%d\t%s\t%s" % (id, name, tips))
