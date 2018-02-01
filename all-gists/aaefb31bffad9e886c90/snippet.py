#!/bin/env python3                                                                               

from flask import Flask
import geoip2.database

app = Flask(__name__)
reader = geoip2.database.Reader('GeoLite2-City.mmdb')

@app.route("/")
def hello():
    return "<h1'>Documentation can go here</h>"
@app.route("/rpt/<value>") #just for testing
def repeat(value):
    return value
@app.route("/<ip>")
def ipfind(ip):
    try:
        response = reader.city(ip)
        country = response.country.name
        area = response.subdivisions.most_specific.name
        city = response.city.name
        thestring = '{}, {}, {}'.format(city, area, country)
        if str(city) == 'None' and str(area) == 'None':
            return ip + '\n' + country + '\n'
        else:
            return ip + '\n' + thestring + '\n'
    except ValueError:
        return "'{}'".format(ip) + " is not a valid IPv4 address. ಠ_ಠ \n"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
