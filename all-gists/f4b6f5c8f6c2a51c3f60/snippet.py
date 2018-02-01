#!/usr/bin/env python

from influxdb import InfluxDBClusterClient

influx_host = "127.0.0.1"
influx_port = 8086
influx_user = "user"
influx_pass = "pass"
database = "example"

influx_timeout = 10
c.influx_max_metrics = 40
c.influx = InfluxDBClusterClient(
             [(influx_host,influx_port)],
             influx_user, influx_pass,
             database, timeout = influx_timeout)


query = c.influx.query("SHOW FIELD KEYS")
values = []

for key,items in query.items():
    for i in list(items):
        values.append(i["fieldKey"])

# String of all mean(values)
# Set makes a uniq list
cq_values = ",".join(map(lambda v: 'mean("%s") AS "%s"' % (v,v), set(values)))

cq_query = 'CREATE CONTINUOUS QUERY {cq_name} ON {database} BEGIN SELECT {cq_values} INTO {database}."rp_{rp}".:MEASUREMENT FROM {database}."{query}"./.*/ GROUP BY time({rp}), * END'

schema = [
        {"rp": "10s", "duration":"2h","query":"default"},
        {"rp": "30s", "duration":"6h","query":"default"},
        {"rp": "1m", "duration":"24h","query":"10s"},
        {"rp": "5m", "duration":"48h","query":"30s"},
        {"rp": "30m", "duration":"7d","query":"5m"},
        {"rp": "1h", "duration":"31d","query":"5m"},
        {"rp": "3h", "duration":"93d","query":"5m"},
        {"rp": "12h", "duration":"370d","query":"1h"},
        {"rp": "24h", "duration":"inf","query":"1h"}
         ]

for s in schema:
    # Create retention policies
    c.influx.create_retention_policy("rp_%s" % s["rp"], s["duration"], "1")

    # Create CQs
    query = cq_query.format(cq_name="%s_cq_%s" % (database,s["rp"]), database=database, cq_values=cq_values, rp=s["rp"], query=s["query"])
    c.influx.query(query)
