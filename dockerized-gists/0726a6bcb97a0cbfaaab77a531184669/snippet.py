# library imports

import pandas as pd
from bokeh.io import output_notebook, show
from bokeh.plotting import figure, output_file, ColumnDataSource
from bokeh.models import HoverTool, BoxAnnotation, BoxSelectTool, BoxZoomTool, WheelZoomTool, ResetTool
from bokeh.resources import CDN
from bokeh.embed import file_html

# Import csv into pandas dataframe, direct to KNIME version to follow

linkdata = pd.read_csv(r'.\output.csv')

df = linkdata[['keyword','slope','searchVolume', 'competition', 'size']]
df = df.rename(columns = {'keyword':'Keyword', 'slope':'Growth',  'searchVolume':'Search Volume', 'competition':'Organic Competition' })
# print(df)

# Bokefy things

source = ColumnDataSource(data=dict(x=df['Organic Competition']*100, y=df['Growth'], desc=df['Keyword'], moredesc=df['Search Volume']))
TOOLS = [HoverTool(tooltips=[("Keyword", "@desc"),("Organic Competition", "@x"),("Growth", "@y"),("Search Volume", "@moredesc")]), BoxZoomTool(), WheelZoomTool(), ResetTool()]

p = figure(plot_width=900, plot_height=600, tools=TOOLS, title="Automated Keyword Research Example", x_axis_label="Organic Competition", y_axis_label="Growth")

# May require playing around with bubble sizing/scaling
p.circle('x', 'y', size=df['Search Volume'], line_color="black", fill_color="orange", source=source)

p.line(df['Organic Competition'].mean()*100, 'y', line_width=5, source=source)
p.line('x', df['Growth'].mean(), line_width=5, source=source)

# Output embeddable, interactive growth matrix for keywords.
html = file_html(p, CDN, "Keyword Research")
output_file = 'embeddable_keyword_research_plot.html'
with open(output_file, 'w') as f:
    f.write(html)

output_notebook()
show(p)