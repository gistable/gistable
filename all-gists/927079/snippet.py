import pyproj

# Define two projections, one for the British National Grid and one for WGS84 (Lat/Lon)
# You can use the full PROJ4 definition or the EPSG identifier (PROJ4 uses a file that matches the two)

#bng = Proj("+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +datum=OSGB36 +units=m +no_defs towgs84='446.448,-125.157,542.060,0.1502,0.2470,0.8421,-20.4894'")
#wgs84 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

bng = pyproj.Proj(init='epsg:27700')
wgs84 = pyproj.Proj(init='epsg:4326')

lon,lat = pyproj.transform(bng,wgs84,439725,557002)

# lon,lat should be now -1.3819797470583639, 54.906163255053869
# which is 53, Fawcett St, Sunderland:
# http://maps.google.com/maps?f=q&source=s_q&hl=en&geocode=&q=54.906163255053869,-1.3819797470583639