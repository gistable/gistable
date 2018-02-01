import forecastio
import datetime
import csv
import time


'''link to the Forecast.io API: https://developer.forecast.io/
   Forecast.io Python Wrapper: https://github.com/ZeevG/python-forecast.io'''


api_key = "Your API Key Goes Here"

'''Locations for weather forecast
	If this list is updated, remember to update the dict keys as well
'''

locations = ['ComEd', 'PECO', 'Duke', 'BGE', 'PPL', 'Dayton', 'JCPL', 'PEPCO', 'Zone A', 'Zone B', 
			 'Zone C', 'Zone D', 'Zone E', 'Zone F', 'Zone G', 'Zone H', 'Zone I', 'Zone J', 'Houston', 'Dallas', 'Laredo']
lats = [41.836828, 39.952335, 39.103118, 39.290385, 41.408969, 39.758948, 40.728157, 38.984652, 42.886447, 43.161030, 
		43.048122, 44.699487, 42.814243, 43.083130, 41.700371, 41.033986, 40.931210, 40.678178, 29.760427, 32.776664, 27.530567  ]
lngs = [-87.640686, -75.163789, -84.512020, -76.612189, -75.662412, -84.191607, -74.077642, -77.094709, -78.878369, -77.610922,  
		-76.147424, -73.452912, -73.939569, -73.784565, -73.920970, -73.762910, -73.898747, -73.944158, -95.369803, -96.796988, -99.480324 ]

''' Location Key
ComEd - Chicago, IL
PECO - Philadelphia, PA
Duke - Cincinnati, OH
BGE - Baltimore, MD
PPL - Scranton, PA
Dayton - Dayton, OH
JCPL - Jersey City, NJ
PEPCO - Bethesda, MD
Zone A - Buffalo, NY
Zone B - Rochester, NY
Zone C - Syracuse, NY
Zone D - Plattsburgh, NY
Zone E - Schenectady, NY
Zone F - Saratoga Springs, NY
Zone G - Poughkeepsie, NY
Zone H - White Plains, NY
Zone I - Yonkers, NY
Zone J - Brooklyn, NY

'''

''' Get the current time to add to the forecast record '''
now = datetime.datetime.now()
ForecastTime = now.strftime("%Y-%m-%d %H:%M")

''' Set the start date to either a specific day or a specific lag '''
#a = datetime.date(2014,12,1)
a = datetime.datetime.today() - datetime.timedelta(1)
numdays = 7 # Set the number of days to pull in the future

'''Set the Date array'''
dateList = []
for x in range (0, numdays):
    dateList.append(a + datetime.timedelta(days = x)) # Can change the '+' to '-' to pull historical

'''Loop through the locations and dates'''
temps = []

for i in range (len(locations)):
	for dates in dateList:
		forecast = forecastio.load_forecast(api_key, lats[i], lngs[i], dates)

		byHour = forecast.hourly()



		for hourlyData in byHour.data:
			try:
				temps.append({
						'ForecastDate': ForecastTime,
						'Time':hourlyData.time.strftime("%Y-%m-%d %H:%M:%S"),
						'Location':locations[i], 
						'Temp':hourlyData.temperature,
						'DewPoint': hourlyData.dewPoint
						}) 
			except:
				pass
				

	

'''Write the results to a csv file'''
keys = ['ForecastDate','Time', 'Location', 'Temp', 'DewPoint']
f = open('WeatherData_Stage.csv', 'wb')
dict_writer = csv.DictWriter(f, keys)
dict_writer.writer.writerow(keys)
dict_writer.writerows(temps)