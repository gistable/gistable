'''
	Written by David Hagan
	January 8, 2015

	This script reads data from the Bacharach ECA 450 Combustion analyzer through the serial interface and 
	logs the data to a file

	In the future (If I ever use the Bacharach again), I aim to convert this into a GUI for ease of use.

	Description of Columns:
	1. TESTID1:		Test ID Line 1
	2. TESTID2: 	Test ID Line 2
	3. TESTDI3: 	Test ID Line 3
	4. FUEL:		Fuel name
	5. TEMP UNIT:	Temperature unit of measure
	6. PRESS UNIT:	Pressure unit of measure
	7. POLL UNIT:	Pollution unit of measure
	8. DATE:		Date of Test
	9. TIME:		Time of Test
	10. O2:			O2 Concentration in %
	11. CO:			CO Concentration
	12. EFF:		Combustion efficiency in %
	13. CO2			CO2 concentration in %
	14. TSTACK		Stack Temperature
	15. TAIR SOURCE	Primary air temperature measurement SOURCE
	16. TAIR		Primary air temperature
	17. EA 			Excess air in %
	18. NO 			NO Concentration
	19. NO2 		NO2 Concentration
	20. NOX			NOx Concentration
	21. SO2			SO2 concentration
	22. HC			Hydrocarbon level in % gas
	23. CO(O2R)		O2 reference for CO
	24. CO(O2) 		CO Concentration referenced to O2
	25. NOX(O2R)	O2 reference for NO, NO2, and NOx in fields 26, 27, and 28
	26. NO(O2)		NO Concentration referenced to O2
	27. NO2(O2R)	NO2 concentration referenced to O2
	28. NOX(O2)		NOx concentration referenced to O2
	29. SO2(O2R)	O2 reference for SO2 in field 30
	30. SO2(O2)		SO2 concentration referenced to O2
	31. PRESSURE 	Pressure (Draft) Measurement
'''

import os
import serial
import datetime
import sys

LOG = True
logDir = False #can also be set to a directory name
filename = 'bacharach-data- ' + str(datetime.datetime.utcnow()) + '.csv'
port = '/dev/tty.usbserial'
baud = 19200
timeout = 20
emptylines = 0

columns = [
	'TESTID1',
	'TESTID2',
	'TESTDI3',
	'FUEL',
	'TEMP UNIT',
	'PRESS UNIT',
	'POLL',
	'DATE',
	'TIME',
	'O2',
	'CO',
	'EFF',
	'CO2',
	'TSTACK',
	'TAIR SOURCE',
	'TAIR',
	'EA',
	'NO',
	'NO2',
	'NOX',
	'SO2',
	'HC',
	'CO(O2R)',
	'CO(O2)',
	'NOX(O2R)',
	'NO(O2)',
	'NO2(O2)',
	'NOX(O2)',
	'SO2(O2R)',
	'SO2(O2)',
	'PRESSURE'
	]

# Change directory
if logDir is not False:
	try:
		os.chdir(logDir)
	except:
		sys.exit("Could not change directories.")


# Connect to serial
try:
	con = serial.Serial(port, baud, timeout=timeout)
except:
	sys.exit("Could not connect to serial. Try checking the port.")


if LOG:
	with open(filename, 'w') as logfile:
		logfile.write(','.join(columns))

		while True and emptylines < 3:
			data = con.readline()
			if len(data) < 3:
				emptylines += 1

			logfile.write(data)

		logfile.close()
		print ("It looks like the data is all written to file")
else:
	while True:
		print con.readline()