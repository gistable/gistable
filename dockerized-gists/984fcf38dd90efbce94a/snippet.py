import numpy as np
import pandas as pd
import datetime
import urllib

from bokeh.plotting import *
from bokeh.models import HoverTool
from collections import OrderedDict

## Read in our data. We've aggregated it by date already, so we don't need to worry about paging

query = ("https://data.lacity.org/resource/mgue-vbsx.json?"
    "$group=date"
    "&call_type_code=507P"
    "&$select=date_trunc_ymd(dispatch_date)%20AS%20date%2C%20count(*)"
    "&$order=date")
raw_data = pd.read_json(query)

## Augment the data frame with the day of the week and the start of the week that it's in.

## This will make more sense soon...

raw_data['day_of_week'] = [date.dayofweek for date in raw_data["date"]]
raw_data['week'] = [(date - datetime.timedelta(days=date.dayofweek)).strftime("%Y-%m-%d") for date in raw_data["date"]]

## Pivot our data to get the matrix we need

data = raw_data.pivot(index='week', columns='day_of_week', values='count')
data = data.fillna(value=0)

## Get our "weeks" and "days"

weeks = list(data.index)
days = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]

## Set up the data for plotting. We will need to have values for every
## pair of year/month names. Map the rate to a color.

max_count = raw_data["count"].max()
day_of_week = []
week = []
color = []
parties = []
for w in weeks:
    for idx, day in enumerate(days):
        day_of_week.append(day)
        week.append(w)
        count = data.loc[w][idx]
        parties.append(count)
        color.append("#%02x%02x%02x" % (255, 255 - (count / max_count) * 255.0, 255 - (count / max_count) * 255.0))

source = ColumnDataSource(
    data=dict(
        day_of_week=day_of_week,
        week=week,
        color=color,
        parties=parties,
    )
)

output_file('all-la-parties.html')

TOOLS = "hover"

p=figure(
    title='\"Party\" Disturbance Calls in LA', 
    x_range=weeks, 
    y_range=list(reversed(days)),
    tools=TOOLS)
p.plot_width=900
p.plot_height = 400
p.toolbar_location='left'

p.rect("week", "day_of_week", 1, 1, source=source, color=color, line_color=None)

p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = np.pi/3

hover = p.select(dict(type=HoverTool))
hover.tooltips = OrderedDict([
    ('parties', '@parties'),
])

show(p) # show the plot