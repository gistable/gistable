# data can be found at https://data.sfgov.org/api/views/tmnf-yvry/rows.csv?accessType=DOWNLOAD
# or https://data.sfgov.org/Public-Safety/SFPD-Incidents-Previous-Three-Months/tmnf-yvry
import time
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas

def classify_day_part(row):
    day_time = time.strptime(data['Time'][row], '%H:%M')
    hour = day_time.tm_hour
    if hour > 5 and hour < 8:
        return 'early morning'
    if hour >= 8 and hour < 12:
        return 'late morning'
    if hour >= 12 and hour <= 15:
        return 'early afternoon'
    if hour <= 16 and hour <= 17:
        return 'late afternoon'
    if hour >=17 and hour <= 19:
        return 'evening'
    if hour >= 20 and hour < 23:
        return 'night'
    if hour >= 23 or hour <= 5:
        return 'late night'

data = pandas.read_csv('SFPD_Incidents_-_Previous_Three_Months.csv')

by_area = data.groupby('PdDistrict')
crimes_by_area = by_area.aggregate({'Category': np.count_nonzero})
unresolved_crimes = data.loc[data['Resolution'] == 'NONE']
unresolved_by_area = unresolved_crimes.groupby('PdDistrict').aggregate({'Category': np.count_nonzero})
unresolved_by_area_percent = [(float(unsolved[0])/total[0]) * 100 for unsolved, total in
                              zip(unresolved_by_area.values, crimes_by_area.values)]
#getting colors                                                                                                                                                                                                                                                            
jet = cm = plt.get_cmap('hot')
cNorm  = colors.Normalize(vmin=0, vmax=len(unresolved_by_area))
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
colors = [scalarMap.to_rgba(i) for i in range(len(unresolved_by_area))]
color_legend = [Patch(color=c[0], label=c[1]) for c in zip(colors, unresolved_by_area.index)]

plt.subplot(2, 2, 1)
plt.scatter(crimes_by_area, unresolved_by_area_percent,s=80, c=colors)
plt.legend(handles=color_legend, loc=4)
plt.title('Total vs unresolved crimes by district')

unresolved_shares = [float(area)/len(unresolved_crimes)* 100 for area in unresolved_by_area.values]

plt.subplot(2, 2, 2)
plt.pie(unresolved_shares, labels= unresolved_by_area.index, colors=colors, autopct='%1.1f%%')
plt.title('Shares of unresolved crimes')

plt.subplot(2, 2, 3)
crime_part_day = data.groupby(classify_day_part)
crime_part_day_agg = crime_part_day.agg({'Category': np.count_nonzero})
crime_day_part_percent = [float(part)/len(data) for part in crime_part_day_agg.values]
plt.pie(crime_day_part_percent, labels= crime_part_day_agg.index, autopct='%1.1f%%')
plt.title('Crimes by part of day')
plt.show()