#!/usr/bin/python

# This script  should be considered CC0 licensed

# the deg2num function is from http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#lon.2Flat_to_tile_numbers_2
import math

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

# x0 = left most Longitutde (minLong)
# y0 = bottom most Latitude (minLat)
# x1 = right most Longitude (maxLong)
# y1 = top most Latitude (maxLat)
def countTiles(minZoom, maxZoom, x0, y0, x1, y1):
    tileCount = 0;

    for z in range(minZoom, maxZoom + 1):
        tiles_dx = ((deg2num(0, x1, z)[0] - deg2num(0, x0, z)[0]) + 1);
        tiles_dy = ((deg2num(y0, 0, z)[1] - deg2num(y1, 0, z)[1]) + 1);
        tileCount +=  tiles_dx * tiles_dy
        #print z, ": ", tiles_dx, ", ", tiles_dy
    
    reportTiles( minZoom, maxZoom, x0, y0, x1, y1, tileCount)

    return tileCount;

def reportTiles(minZoom, maxZoom, x0, y0, x1, y1, totalTiles):

    print "Geographic area:"
    print "\t%f\tleft most Longitude (minLong)" % x0
    print "\t%f\tbottom most Latitude (minLat)" % y0
    print "\t%f\tright most Longitude (maxLong)" % x1
    print "\t%f\ttop most Latitude (maxLat)" % y1
    
    print "Zoom coverage:"
    print "\t%.0f\tleast detailed zoom" % minZoom
    print "\t%.0f\tmost detailed zoom" % maxZoom
    
    print "Total tiles:"
    print "\t%.0f" % totalTiles
  
def estimateAmazon( tiles ):
    averageTileSizeKB = 20
    
    totalSizeGB = tiles * averageTileSizeKB / (1024*1024)

    print "Total size (at an average of %dKB per tile):" % (averageTileSizeKB)
    print "\t%.2f GB" % (totalSizeGB)

    # To store it, monthly
    # http://aws.amazon.com/s3/pricing/
    # US region
    s3_pricingPerGB = 0.125         # $ / gb
    
    s3_storageCost = totalSizeGB * s3_pricingPerGB
    
    # to seed it, once
    # http://aws.amazon.com/s3/pricing/
    # $0.01 per  1,000 requests
    s3_postingCostPerRequest = .01 / 1000
    
    s3_postingCost = tiles * s3_postingCostPerRequest
    
    print "\nSETUP cost: $%.2f" % (s3_storageCost + s3_postingCost)
    print "(One time cost: $%.2f storage, $%.2f posting)" % (s3_storageCost, s3_postingCost)
    print "(Note: If there is a data update, apply this setup cost again.)"
    print "\nMONTHLY viewing costs:"
    
    # For viewing costs (linear), monthly
    # http://aws.amazon.com/s3/pricing/
    # $0.01 per  10,000 requests
    s3_viewingCostPerRequest = .01 / 10000
    
    # For viewing costs (linear), monthly
    # http://aws.amazon.com/s3/pricing/
    # $0.12 per GB aftr first 1GB (free)
    s3_viewingCostPerGB = 0.120
    
    approxTilesPerVisior = 200
    
    for visits in (10000, 250000, 1000000, 10000000):
    
        requests = approxTilesPerVisior * visits
    
        s3_viewingCost = requests * s3_viewingCostPerRequest
        
        # subtract 1 because first 1GB looks to be free
        tileSizeGB = averageTileSizeKB / float(1024 * 1024)
        s3_viewingCost += max(tileSizeGB * requests - 1, 0) * s3_viewingCostPerGB
        
        cf_viewingCost = s3_viewingCost * 2
        
        print "%010s visits: $%.2f,\twith cloudfront: $%.2f" % (str(visits), s3_viewingCost, cf_viewingCost)
    
    print "\n(Assumption: Each map visitor will request %.0f tiles (load map, pan pan pan pan pan)" % approxTilesPerVisior
    print "(Note: CloudFront is a distributed content delivery network that makes viewing your tiles faster..."
    print "\tAmazon charges once for getting it out of the S3 bucket and into CF again for the CF view..."
    print "\tIf all the views are in the same spot, 1/2 the CF cost listed here. If viewing many random\n\tplaces,this value.)"

if __name__ == "__main__" :
    import optparse
    
    parser=optparse.OptionParser( usage='%prog "minZoom, maxZoom, x0, y0, x1, y1"' )
    
    options, args = parser.parse_args()
    
    if len( args ) == 0 :
        # CONUS United States (excluding Alaska and Hawaii)
        estimateAmazon( countTiles(4, 14, -126.9, 22.2, -67.2, 50.0) )
    else :
        try:
            minZoom, maxZoom, x0, y0, x1, y1 = map(float, args[0].split(', '))
            estimateAmazon( countTiles( int(minZoom), int(maxZoom), x0, y0, x1, y1 ) )
        except Exception, e:
            print "Couldn't parse arguments: %s" % e
            parser.print_usage()
