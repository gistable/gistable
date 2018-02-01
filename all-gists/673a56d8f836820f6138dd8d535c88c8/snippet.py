#!/usr/local/bin/python

# encoding: utf-8
"""
collect_kostal.py

Created by Christian Stade-Schuldt on 2014-07-27.
"""

import urllib2
import datetime

from lxml import html
import sqlite3


URL = 'http://192.168.1.125' # use your address
USERNAME = 'your_username'
PASSWORD = 'your_password'


def get_data():
    """reads the data from the kostal inverter"""

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

    top_level_url = URL
    username = USERNAME
    password = PASSWORD
    password_mgr.add_password(None, top_level_url, username, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)

    opener = urllib2.build_opener(handler)
    opener.open(URL)

    urllib2.install_opener(opener)
    response = urllib2.urlopen(URL)
    root = html.fromstring(response.read().strip())
    data = [v.text.strip() for v in root.xpath("//td[@bgcolor='#FFFFFF']")]

    current_power = data[0]
    total_energy = data[1]
    daily_energy = data[2]
    dc_u_1 = data[3]
    ac_u_1 = data[4]
    dc_i_1 = data[5]
    ac_p_1 = data[6]
    dc_u_2 = data[7]
    ac_u_2 = data[8]
    dc_i_2 = data[9]
    ac_p_2 = data[10]
    dc_u_3 = data[11]
    ac_u_3 = data[12]
    dc_i_3 = data[13]
    ac_p_3 = data[14]

    data = [dc_u_1, dc_i_1, ac_u_1, ac_p_1, dc_u_2, dc_i_2, ac_u_2, ac_p_2, dc_u_3, dc_i_3, ac_u_3, ac_p_3,
            current_power, daily_energy, total_energy]
    return data


def save_data_to_db(data):
    """saves the data tuple to the database"""
    con = sqlite3.connect("PATH_TO_SQLITE_FILE")

    con.isolation_level = None
    cur = con.cursor()

    query = '''INSERT INTO pvdata VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

    cur.execute(query, tuple([datetime.datetime.now().isoformat()] + data))

    con.commit()
    con.close()


def is_number(s):
    """checks if input is a valid number """
    try:
        int(s)
        return True
    except ValueError:
        return False


def main():
    data = get_data()
    if is_number(data[0]):
        save_data_to_db(data)


if __name__ == '__main__':
    main()