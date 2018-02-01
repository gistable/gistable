"""
Web Mercator Scale and Resolution Calculations
Python implementation of the formulas at http://msdn.microsoft.com/en-us/library/bb259689.aspx
"""
import math

def meters_per_pixel(zoom, lat):
    """
    ground resolution = cos(latitude * pi/180) * earth circumference / map width
    """
    return (math.cos(lat * math.pi/180.0) * 2 * math.pi * 6378137) / (256 * 2**zoom)

def map_scale(zoom, lat, dpi=96.0):
    """
    map scale = 1 : ground resolution * screen dpi / 0.0254 meters/inch
    """
    res = meters_per_pixel(zoom, lat)
    return (res * dpi) / 0.0254

if __name__ == "__main__":
    tests = [ (5, 45.0), 
              (12, 0.0), 
              (12, 79.0)]

    for test in tests:
        print "Zoom %d at latitude %f => %f meters per pixel (scale is 1:%d at 96 dpi)" % (test[0], 
                test[1], meters_per_pixel(*test), map_scale(*test))
