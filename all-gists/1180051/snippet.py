'''
aero님께서 구현하신 구글/네이버/싸이월드/콩나물 좌표변환은 펄/자바스크립트로 되어있습니다.
펄/자바스크립트에 익숙지 않은지라, 수식을 파이썬으로 번역해보았습니다.
'''

from pyproj import Proj
from pyproj import transform

WGS84 = { 'proj':'latlong', 'datum':'WGS84', 'ellps':'WGS84', }

# conamul
TM127 = { 'proj':'tmerc', 'lat_0':'38N', 'lon_0':'127.0028902777777777776E',
   'ellps':'bessel', 'x_0':'200000', 'y_0':'500000', 'k':'1.0',
   'towgs84':'-146.43,507.89,681.46'}

# naver
TM128 = { 'proj':'tmerc', 'lat_0':'38N', 'lon_0':'128E', 'ellps':'bessel',
   'x_0':'400000', 'y_0':'600000', 'k':'0.9999',
   'towgs84':'-146.43,507.89,681.46'}

# GRS80(Geodetic Reference System 1980：측지 기준계 1980)의 타원체
GRS80 = { 'proj':'tmerc', 'lat_0':'38', 'lon_0':'127', 'k':1, 'x_0':200000,
    'y_0':600000, 'ellps':'GRS80', 'units':'m' }

def wgs84_to_tm128(longitude, latitude):
   return transform( Proj(**WGS84), Proj(**TM128), longitude, latitude )

def tm128_to_wgs84(x, y):
   return transform( Proj(**TM128), Proj(**WGS84), x, y )

def wgs84_to_tm127(longitude, latitude):
   return map(lambda x:2.5*x,
        transform( Proj(**WGS84), Proj(**TM127), longitude, latitude ))

def tm127_to_wgs84(x, y):
   return transform( Proj(**TM127), Proj(**WGS84), x/2.5, y/2.5 )

def grs80_to_wgs84(x, y):
   return transform( Proj(**GRS80), Proj(**WGS84), x, y )

def wgs84_to_cyworld(longitude, latitude):
   x_min = 4456260.72
   y_min = 1161720.00
   long_min = 123.78323
   lat_min = 32.27345
   max_grid_length = 112721.92
   x = (longitude-long_min)*max_grid_length/3.1308 + x_min
   y = (latitude-lat_min)*max_grid_length/3.1308 + y_min
   return x, y

def cyworld_to_wgs84(x, y):
   x_min = 4456260.72;
   y_min = 1161720.00;
   long_min = 123.78323;
   lat_min = 32.27345;
   max_grid_length = 112721.92;
   longitude = long_min + (x-x_min)*3.1308 / max_grid_length;
   latitude = lat_min + (y-y_min)*3.1308 / max_grid_length;
   return longitude, latitude