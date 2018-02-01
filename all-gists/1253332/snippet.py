#coding:utf-8
"""
unofficial Google Weather API

http://www.google.com/ig/api?weather=,,,35693692,139700260&hl=ja

レスポンスのエンコーディングは hl=jaの場合Shift-JIS hl=enの場合ASCII
<xml_api_reply version="1">
  <weather module_id="0" tab_id="0" mobile_row="0" mobile_zipped="1" row="0" section="0">
    <forecast_information>
      <city data=""/>
      <postal_code data=""/>
      <latitude_e6 data="35693692"/>
      <longitude_e6 data="139700260"/>
      <forecast_date data="2011-09-30"/>
      <current_date_time data="2011-09-30 03:00:00 +0000"/>
      <unit_system data="SI"/>
    </forecast_information>
    <current_conditions>
      <condition data="曇り"/>
      <temp_f data="82"/>
      <temp_c data="28"/>
      <humidity data="湿度 : 51%"/>
      <icon data="/ig/images/weather/jp_cloudy.gif"/>
      <wind_condition data="風: 南西 2 m/s"/>
    </current_conditions>
    <forecast_conditions>
      <day_of_week data="金"/>
      <low data="20"/>
      <high data="29"/>
      <icon data="/ig/images/weather/jp_sunnythencloudy.gif"/>
      <condition data="晴のち曇"/>
    </forecast_conditions>
"""

import urllib
from xml.etree import ElementTree
from dateutil import parser as date_parser
import re

def get_current(lat, lng):
    """ 座標から最寄りの近い地点の天候、湿度、風速、風向を取得する"""
    base_url = 'http://www.google.com/ig/api?weather=,,,%d,%d&hl=ja'
    lat_e6 = e6(lat)
    lng_e6 = e6(lng)
    url = base_url % (lat_e6, lng_e6)
    xml_string = urllib.urlopen(url).read()
    xml_string = xml_string.decode("shift_jis").encode("utf-8")
    xml = ElementTree.fromstring(xml_string)
    current = xml.find('.//current_conditions')
    condition = current.find('./condition').attrib['data']
    temp = current.find('./temp_c').attrib['data']
    if temp:
        temp = float(temp)
    hum = current.find('./humidity').attrib['data']
    humidity = None
    if hum:
        hum_match = re.search('(\d{1,2})%', hum)
        if hum_match:
            humidity = float(hum_match.group(1))
    wind = current.find('./wind_condition').attrib['data']
    return condition, temp, wind, humidity


def e6(value):
    """Google Weatehr APIで使用する小数点以下6桁まで表示し、
    小数点を消去するフォーマットを返す

    >>> e6(35.69369)
    35693690
    """
    head, tail = str(value).split('.')
    tail = '%s000000' % tail
    return int('%s%s'%(head, tail[:6]))


print get_current(35.70,139.58)
