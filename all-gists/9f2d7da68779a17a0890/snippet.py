#!/usr/bin/env python

from csvkit.convert.js import json2csv
from collections import OrderedDict
from flask import Flask
import rethinkdb as r
import json, StringIO

config = {
    "port": 8096,
    "host": "0.0.0.0",
    "database": {
        "host": "localhost",
        "port": 28015,
        "db": "quake"
    }
}

app = Flask(__name__)

feedUrl = "earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"
refresh = r.table("quakes").insert(r.http(feedUrl)["features"], conflict="replace")

try:
    conn = r.connect(**config["database"])
    r.db_create(config["database"]["db"]).run(conn)
    r.table_create("quakes").run(conn)
    refresh.run(conn)
except Exception as e:
    if "already exists" not in e.message: print e
finally: conn.close()

@app.route("/quakes")
def quakesJSON():
    conn = r.connect(**config["database"])
    output = r.table("quakes") \
                .group(r.epoch_time(r.row["properties"]["time"] / 1000).date()) \
                .ungroup().merge({"count": r.row["reduction"].count()}) \
                .run(conn)

    conn.close();
    return json.dumps([OrderedDict([
        ["date", item["group"].strftime("%D")],
        ["count", item["count"]]]) for item in output])

@app.route("/quakes/csv")
def quakesCSV():
    return json2csv(StringIO.StringIO(quakesJSON()))

if __name__ == "__main__":
    app.run(host=config["host"], port=config["port"], debug=True)
