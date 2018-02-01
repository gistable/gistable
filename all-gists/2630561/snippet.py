#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

from subprocess import Popen, PIPE

def ioreg_battery_info():
    output = Popen(["ioreg", "-r", "-k", "LegacyBatteryInfo", "-w", "0"], stdout=PIPE).communicate()[0]
    try: #python3
        return str(output, encoding='utf-8')
    except TypeError: #python2
        return output

def parse_ioreg_dict(output):
    return dict(
            [ (kw.strip().strip('"'), vw.strip())
              for kw, vw
              in [ line.split("=", 1)
                   for line
                   in output.split('\n') if line.find('=')>0
                 ]
            ]
           )

def is_two_complement_negative(value):
    return value > (2**63-1)

def two_complement(value):
    return 2**64 - value

def fix_negative(value):
    if is_two_complement_negative(value):
        return -two_complement(value)
    else:
        return value

def ioreg_battery_dict():
    output = ioreg_battery_info()
    return parse_ioreg_dict(output)


def fix_integer(string):
    return fix_negative(int(string))

def format_time(string):
    minutes = int(string)
    if minutes == 65535:
        return None
    else:
        return "%s:%s" % (minutes//60, minutes%60)

def percentage(ratio):
    return "%s%%" % (int(ratio*100))

humanize_index = {
        "TimeRemaining": format_time,
        "AvgTimeToEmpty": format_time,
        "AvgTimeToFull": format_time,
        "InstantTimeToEmpty": format_time,
        "FullToEmptyTime": format_time,
        "WearRatio": percentage,
        "ChargeRatio": percentage,
        }

def humanize_data(k, v):
    if k in humanize_index:
        return humanize_index[k](v)
    else:
        return v

def wear_ratio(info):
    return int(info["MaxCapacity"]) / int(info["DesignCapacity"])

def charge_ratio(info):
    return int(info["CurrentCapacity"]) / int(info["MaxCapacity"])

def full_to_empty_time(info):
    if get_data(info, "Amperage") < 0:
        return -int(info["MaxCapacity"])*60 / get_data(info, "Amperage")
    else:
        return 65535

synthetize_index = {
        "Amperage": lambda i: fix_integer(i["Amperage"]),
        "InstantAmperage": lambda i: fix_integer(i["InstantAmperage"]),
        "WearRatio": wear_ratio,
        "ChargeRatio": charge_ratio,
        "FullToEmptyTime": full_to_empty_time,
        }

def synthetize_data(battery_info, k):
    if k in synthetize_index:
        return synthetize_index[k](battery_info)

def get_data(battery_info, k):
    if k in synthetize_index:
        return synthetize_data(battery_info, k)
    elif k in battery_info:
        return battery_info[k]
    else:
        raise KeyError("%s" % k)

keys_to_show = [
        "Temperature",
        "CycleCount",
        #"DesignCycleCount9C",
        "DesignCapacity",
        "MaxCapacity",
        "WearRatio",
        "CurrentCapacity",
        "ChargeRatio",
        "Voltage",
        "Amperage",
        "InstantAmperage",
        "InstantTimeToEmpty",
        "TimeRemaining",
        "AvgTimeToEmpty",
        "AvgTimeToFull",
        "FullToEmptyTime",
        ]

def print_key_value(k, v):
    if v is not None:
        print("%s = %s" % (k, v))

battery_info =  ioreg_battery_dict()

for k in keys_to_show:
    print_key_value(k, humanize_data(k, get_data(battery_info, k)))
