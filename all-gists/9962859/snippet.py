#!/usr/bin/python
"""
Get number of RSVPs for #Iot Day and send them to Ubidots

"""

__author__ = "Agustin Pelaez"

from sys import argv
import ubidots
import requests
import time

def get_var_by_name(var_name, ds):
    """Search for a variable in a datasource. If found, returns the variable.
   If not found, returns None."""
    for var in ds.get_variables():

        if var.name == var_name:
            return var

    return None

if __name__ == "__main__":

    old_rsvp = 0

    while(1):
        if len(argv) < 2:
            print "Usage: %s API_KEY" % argv[0]
            sys.exit(0)

        api = ubidots.ApiClient(argv[1])

        # Search for a data source with name matching the desired
        # name of our datasource. If it doesn"t exist, create it.
        ds_name = "Meetup.com"
        ds = None
        var_name = "RSVPs IoT Hackday"
        var = None

        for cur_ds in api.get_datasources():
            if cur_ds.name == ds_name:
                ds = cur_ds
                break

        if ds is None:
            ds = api.create_datasource({"name": ds_name})

        # Create a variable

        for cur_var in api.get_variables():
            if cur_var.name == var_name:
                var = cur_var
                break

       if var is None:
            var = ds.create_variable({"name": var_name, "unit": "users"})

        # Get users data

        meetup_event = requests.get('http://api.meetup.com/2/event/174983242?key=xxxxxxxx484c7015486e21xxxxxx')
        rsvp = meetup_event.json().get('yes_rsvp_count')
        print rsvp

        # Send data to Ubidots

        if rsvp != old_rsvp:
            var.save_value({"value": rsvp})

        old_rsvp = rsvp
        time.sleep(1)
