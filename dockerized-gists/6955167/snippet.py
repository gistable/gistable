import requests
import json
import pprint
import xml.etree.ElementTree as ET
import argparse
from fabulous import image
from StringIO import StringIO


def find_intersections(lines):
    """
    Parse a javascript file that contains a list of json encoded
    intersections. Return a decoded python dict with that info
    :param lines: The lines from the js file
    :type lines: list
    """
    ints = []
    for line in lines:
        line = line.strip()
        if '"iInfo"' in line:
            if line.endswith(','):
                line = line[:-1]
            ints.append(line)
    return ints

def grab_js():
    """
    Do a get request to the sccgov website to get the rdatraffic
    javascript source
    """
    return requests.get("http://eservices.sccgov.org/rdalivetraffic/javascript/rdatraffic.js").text.split('\n')


def generate_proxy_url(*ids):
    """
    Generate a proxy url to get the trafficland information using the
    government proxy server
    :param ids: The ids to generate a proxy url for
    """
    return "http://eservices.sccgov.org/rdalivetraffic/SccgovGenericWebServiceProxy.ashx?s=trafficland&id=&{0}".format("&".join(['id={0}'.format(i) for i in ids]))

class Camera(object):
    def __init__(self, city_code, name, orient, provider, refresh_rate, temp_dis, web_id, location):
        self.city_code = city_code
        self.name = name
        self.orient = orient
        self.provider = provider
        self.refresh_rate = refresh_rate
        self.temp_dis = temp_dis
        self.web_id = web_id
        self.location = location
        self.half_image = ''
        self.full_image = ''

    def update_urls(self, half='', full=''):
        self.half_image = half
        self.full_image = full

def parse_proxy_response(xmlstring):
    """
    Take the xml response to a proxy request and turn it into a list
    of python objects containing all the info needed to view cameras
    """
    root = ET.fromstring(xmlstring)
    cameras = []
    for camera in root.iter('camera'):
        cityCode = camera.attrib['cityCode']
        name = camera.attrib['name']
        orientation = camera.attrib['orientation']
        provider = camera.attrib['provider']
        refreshRate = camera.attrib['refreshRate']
        tempdis = camera.attrib['tempdis']
        webid = camera.attrib['webid']

        loc_elem = camera.find('location')
        location = (loc_elem.attrib['latitude'], loc_elem.attrib['longitude'], loc_elem.attrib['zipCode'])

        half = camera.find('halfimage')
        full = camera.find('fullimage')
        new_cam = Camera(cityCode, name, orientation, provider, refreshRate, tempdis, webid, location)
        if half is not None:
            new_cam.update_urls(half=half.text)
        if full is not None:
            new_cam.update_urls(full=full.text)
        cameras.append(new_cam)
    return cameras


def main():
    """
    Run the program to grab camera data from the sccgov website
    """
    script = grab_js()
    ints = find_intersections(script)
    parsed_ints = map(json.loads, ints)
    int_dict = {}
    for inter in parsed_ints:
        iinfo = inter['iInfo']
        int_dict[iinfo['intersection']] = iinfo
    pprint.pprint(int_dict)

    parser = argparse.ArgumentParser()
    parser.add_argument("--inter", help='The intersection to look at')
    parser.add_argument("--orient", help='The orientation to look at')
    args = parser.parse_args()
    if args.inter in int_dict:
        inter = int_dict[args.inter]
        if args.orient in inter:
            cam_id = inter[args.orient]
            proxy_url = generate_proxy_url(cam_id)
            xmlstring = requests.get(proxy_url).text
            cameras = parse_proxy_response(xmlstring)
            print image.Image(StringIO(requests.get(cameras[0].full_image).content))


if __name__ == "__main__":
    main()