from matplotlib.dates import HourLocator, DateFormatter, date2num
from datetime import timedelta

start = df.index.min()
end = df.index.max()

delta = timedelta(hours=1)
dates = matplotlib.dates.drange(start, end, delta)

lines = df.pageviews, df.visitors
colours = ['steelblue', 'coral']
direct_labels = [(-10,10), (10,-10)]
series_names = ['pageviews', 'visitors']

def addLabels(x_y_tuples, axis, offset_by):
    txt_fmt = 'offset points'

    for i, tup in enumerate(x_y_tuples):
		if i % 2 == 0:
			x = tup[0]
			y = tup[1]
			axis.annotate(str(int(y)), (x,y), 
				xytext=offset_by, textcoords=txt_fmt)

fig = figure(figsize=(14,6))
ax = fig.add_subplot(111)

for y, colour, offset, series_name in zip(lines, colours, direct_labels, series_names):
    points = zip(map(lambda x: date2num(x), df.index), y)
    ax.plot_date(dates, y, '.-', linestyle='-', marker='.', linewidth=1.0, color=colour, label=series_name)
    addLabels(points, axis=ax, offset_by=offset)
    ax.set_xlim( dates[0], dates[-1] )

ax.xaxis.set_minor_locator( HourLocator(arange(0,25,6)) )
ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
fig.autofmt_xdate()
ax.xaxis.grid(True, 'major')
ax.xaxis.grid(False, 'minor')
ax.grid(True)
plt.legend()
show()