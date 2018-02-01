# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import argparse

banner = """
_________ _______   _________ _______  _______  _______  _        _______  _______ 
\__   __/(  ____ )  \__   __/(  ____ )(  ___  )(  ____ \| \    /\(  ____ \(  ____ )
   ) (   | (    )|     ) (   | (    )|| (   ) || (    \/|  \  / /| (    \/| (    )|
   | |   | (____)|     | |   | (____)|| (___) || |      |  (_/ / | (__    | (____)|
   | |   |  _____)     | |   |     __)|  ___  || |      |   _ (  |  __)   |     __)
   | |   | (           | |   | (\ (   | (   ) || |      |  ( \ \ | (      | (\ (   
___) (___| )           | |   | ) \ \__| )   ( || (____/\|  /  \ \| (____/\| ) \ \__
\_______/|/            )_(   |/   \__/|/     \|(_______/|_/    \/(_______/|/   \__/
-----------------------------------------------------------------------------------\n
"""

def show_result(infos):
    show_infos = (
                "IP: {0}\n".format(infos["IP Address"]) +
                "Longitude: {0}\n".format(infos["Longitude"]) +
                "Latitude: {0}\n".format(infos["Latitude"])+
                "Cidade: {0}\n".format(infos["City"]) +
                "Região: {0}\n".format(infos["Region"]) +
                "Horário Local: {0}\n".format(infos["Local time"]) +
                "País: {0}".format(infos["Country Code"])
    )
    print banner + show_infos

def define_command_line_parse():
    parser = argparse.ArgumentParser(
        description="Get informations of IP address.")
    parser.add_argument('-i', '--ip', help="IP to get informations")
    args = parser.parse_args()
    if args.ip:
        get_data(args.ip)
    else:
        print banner
        parser.print_help()

def get_data(ip_adress):
    url = "http://www.geoiptool.com/en/?ip="+ip_adress
    response = urllib2.urlopen(url)
    if response.code == 200:
        infos = search_information(response.read())
        return show_result(infos)
    return None

def search_information(data):
    if data is not None:
        informations = BeautifulSoup(data)
        data_ip = informations.findAll(
            "div", 
            {"class" : "sidebar-data hidden-xs hidden-sm"}
        )
        return take_information(data_ip)

def take_information(bs_data_found):
    data = bs_data_found[0]
    all_informations = data.findAll("span")
    dict_data = {}
    i=0
    while i < len(all_informations):
        key = str(all_informations[i].string).replace(":","")
        value = str(all_informations[i+1].string)
        dict_data[key] = value
        i+=2
    return dict_data

define_command_line_parse()
