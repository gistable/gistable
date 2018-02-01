#!/usr/bin/env python

import urllib2
import json
import plotly
import datetime
import plotly.plotly as py

from plotly.graph_objs import *
py.sign_in('XXXX', 'XXXX')


api_key = 'XXXX'
sf_lookup_url = 'http://api.wunderground.com/api/' + api_key + '/geolookup/conditions/q/CA/San_Francisco.json'
mtl_lookup_url = 'http://api.wunderground.com/api/' + api_key + '/conditions/q/Canada/Montreal.json'


urls = { 'MTL': mtl_lookup_url, 'SF': sf_lookup_url }
temps = { 'MTL': [], 'SF': [] }

for city in temps.keys():
    f = urllib2.urlopen(urls[city])
    json_string = f.read()
    parsed_json = json.loads(json_string)
    temps[city].append( parsed_json['current_observation']['temp_c'] )
    temps[city].append( parsed_json['current_observation']['temp_f'] )
    # print "Current temperature in %s is: %s C, %s F" % (city, temps[city][0], temps[city][1] )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    f.close()

layout = Layout(
    title='Current temperature in Montreal and San Francisco',
    titlefont=Font(
        family='"Open sans", verdana, arial, sans-serif',
        size=17,
        color='#444'
    ),
    font=Font(
        family='"Open sans", verdana, arial, sans-serif',
        size=12,
        color='#444'
    ),
    showlegend=True,
    autosize=True,
    width=803,
    height=566,
    xaxis=XAxis(
        title='Click to enter X axis title',
        titlefont=Font(
            family='"Open sans", verdana, arial, sans-serif',
            size=14,
            color='#444'
        ),
        range=[1418632334984.89, 1418632334986.89],
        domain=[0, 1],
        type='date',
        rangemode='normal',
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        autotick=True,
        nticks=0,
        ticks='inside',
        showticklabels=True,
        tick0=0,
        dtick=1,
        ticklen=5,
        tickwidth=1,
        tickcolor='#444',
        tickangle='auto',
        tickfont=Font(
            family='"Open sans", verdana, arial, sans-serif',
            size=12,
            color='#444'
        ),
        mirror='allticks',
        linecolor='rgb(34,34,34)',
        linewidth=1,
        anchor='y',
        side='bottom'
    ),
    yaxis=YAxis(
        title='Temperature (degrees)',
        titlefont=Font(
            family='"Open sans", verdana, arial, sans-serif',
            size=14,
            color='#444'
        ),
        range=[-5.968375815056313, 57.068375815056314],
        domain=[0, 1],
        type='linear',
        rangemode='normal',
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        autotick=True,
        nticks=0,
        ticks='inside',
        showticklabels=True,
        tick0=0,
        dtick=1,
        ticklen=5,
        tickwidth=1,
        tickcolor='#444',
        tickangle='auto',
        tickfont=Font(
            family='"Open sans", verdana, arial, sans-serif',
            size=12,
            color='#444'
        ),
        exponentformat='B',
        showexponent='all',
        mirror='allticks',
        linecolor='rgb(34,34,34)',
        linewidth=1,
        anchor='x',
        side='left'
    ),
    legend=Legend(
        x=1,
        y=1.02,
        traceorder='normal',
        font=Font(
            family='"Open sans", verdana, arial, sans-serif',
            size=12,
            color='#444'
        ),
        bgcolor='rgba(255, 255, 255, 0.5)',
        bordercolor='#444',
        borderwidth=0,
        xanchor='left',
        yanchor='auto'
    )
)

cur_time = datetime.datetime.now() # current date and time                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
data=[]
temp_types = ['C','F']
for city in temps.keys():
    for i in range(len(temp_types)):
        data.append( Scatter( x=[cur_time], y=[temps[city][i]], \
                             line=Line(dash='dot') if i==0 else Line(),
                             mode='lines+markers', \
                             name='{0} ({1})'.format(city,temp_types[i]) ) )

data = Data( data )
fig = Figure(data=data, layout=layout)
plot_url=py.plot(fig, filename='montreal-and-san-francisco-temperatures',fileopt='extend',auto_open=False)
# print plot_url                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

