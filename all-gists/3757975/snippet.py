# python plotter.py test.csv => will produce test.png
# Give it a csv file as argument and it will produce a png image with the same name as the csv file
# It expects the CSV file to be of format '2012-09-20 20:32,1.3,2.1'
# NOTE: This code will show the graph so you need a gui builder. It will fail on a server

# TO make it run on a server use 'Agg'
# import matplotlib
# matplotlib.use('Agg')
# and don't use the show() method


import csv
import datetime
import matplotlib.pyplot as plt
from dateutil.parser import parse
import sys
from matplotlib.dates import date2num
import datetime as DT

csv_file = sys.argv[1]
image_file = csv_file[:-3]+"png"

y,x,xticks,y_max = [],[],[],[]
csv_reader = csv.reader(open(csv_file))
for line in csv_reader:
	x.append(DT.datetime.strptime(line[0], "%Y-%m-%d %H:%M")) # %H:%M:%S
	xticks.append(line[0])
	y.append(float(line[1]))
	y_max.append(float(line[2]))


fig = plt.figure()
ax = fig.add_subplot(111)
fig.subplots_adjust(bottom=0.35)

date_as_numbers = [date2num(date) for date in x]
ax.plot(date_as_numbers,y)
ax.plot(date_as_numbers,y_max)

plt.xticks(x,xticks)
plt.xticks(rotation='vertical')
plt.show()

#fig.autofmt_xdate()
fig.savefig(image_file)