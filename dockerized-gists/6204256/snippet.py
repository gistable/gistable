"""
Convert LocationHistory.json from Google takeout of location history (latitude)
to a usable KML file for viewing in Google Earth.


Usage: 

    python json_history_to_kml.py LocationHistory.json



Example kml output:
    <?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Placemark>
        <name>Simple placemark</name>
        <description>Attached to the ground. Intelligently places itself 
           at the height of the underlying terrain.</description>
        <Point>
          <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
        </Point>
      </Placemark>
    </kml>

Example JSON input:
    {
      "locations" : [ {
        "timestampMs" : "1373570050813",
        "latitudeE7" : 320946855,
        "longitudeE7" : 347981459,
        "accuracy" : 53
      },
    }


"""

import sys
import json
import time
import os

DAYS_DIR = 'kmldays'

loc_fmt = """
      <Placemark>
        <name>{name}</name>
        <description>{description}</description>
        <Point>
          <coordinates>{coordinates}</coordinates>
        </Point>
      </Placemark>"""

kml_start = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>"""

kml_end ="""
</Document>
</kml>"""


class KML:
    def __init__(self, fn):
        self.fn = fn
        self.fhand = open(self.fn, 'wb')
        self.fhand.write(kml_start)
        self.to_close = []
        
    def close(self):
        while len(self.to_close) > 0:
            self._close_one()
        self.fhand.write(kml_end)
        self.fhand.close()
    
    def _indent(self):
        return '  ' * len(self.to_close)
    
    def _node(self, node):
        spaces = self._indent()
        self._line('<%s>' % node)
        self.to_close.append('\n%s</%s>' % (spaces, node))
    
    def _line(self, text):
        self.fhand.write('\n%s%s' % (self._indent(), text))
    
    def Folder(self, name):
        self._node('Folder')
        self._line('<name>%s</name>' % name)
        self._line('<visibility>0</visibility>')
        
    def NetworkLink(self, name, fn):
        self._node('NetworkLink')
        self._line('<name>%s</name>' % name)
        self._line('<visibility>0</visibility>')
        self._line('<Link><href>%s</href></Link>' % fn)
        self._close_one()
        
    def PlaceMark(self, name, description, lat, lon):
        coord_str = "%s,%s,0" % (lon, lat)
        node = loc_fmt.format(name=name,
                              description=description,
                              coordinates=coord_str)
        self.fhand.write(node)
    
    def _close_one(self, expected=None):
        text = self.to_close.pop()
        if expected is not None:
            if not expected in text:
                raise Exception("Expected to close '%s' but found '%s'" % (expected, text))
        self.fhand.write(text)
    


def main():
    fn = sys.argv[1]
    
    days_dir = os.path.join(os.path.dirname(fn), DAYS_DIR)
    
    if not os.path.exists(days_dir):
        os.mkdir(days_dir)
    
    out_fn = fn + '.kml'
    print('loading json')
    data = json.load(open(fn))
    locations = data['locations']
    cur_year = None
    cur_day = None
    day_kml = None
    print('handling %d points' % len(locations))
    
    kml = KML(out_fn)
    for i, loc in enumerate(locations):
        time_s = float(loc['timestampMs']) / 1e3
        lat = float(loc['latitudeE7']) / 1e7
        lon = float(loc['longitudeE7']) / 1e7
        coord_str = "%s,%s,0" % (lon, lat)
        acc = loc.get('accuracy', 'n/a')
        tm = time.gmtime(time_s)
        date_str = time.strftime("%Y-%m-%d", tm)
        time_str = time.strftime("%Y-%m-%d %a %H:%M:%S", tm)
        desc_str = 'accuracy %s meters' % acc

        if i % 1000 == 0:
            sys.stdout.write('.')

        if date_str != cur_day:
            if i != 0:
                #break
                #kml._close_one('Folder') # previous day
                day_kml.close()

            if tm.tm_year != cur_year:
                if i != 0:
                    kml._close_one('Folder') # previous year

                cur_year = tm.tm_year
                kml.Folder(name=str(cur_year))

            cur_day = date_str
            #kml.Folder(name=str(date_str))
            day_fn = os.path.join(days_dir, date_str + '.kml')
            day_kml = KML(day_fn)
            kml.NetworkLink(name=date_str, fn=day_fn)


        #fhand.write(node)
        name = time_str
        description = desc_str
        coordinates = coord_str
        day_kml.PlaceMark(name, description, lon=lon, lat=lat)

    kml.close()
        
        

if __name__ == "__main__":
    main()


