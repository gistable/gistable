import math
import os
import urllib
from shapely.geometry import Polygon

def deg2num(lat_deg, lon_deg, zoom):
	lat_rad = math.radians(lat_deg)
	n = 2.0 ** zoom
	xtile = int((lon_deg + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
	return (xtile, ytile)
	
def num2deg(xtile, ytile, zoom):
	n = 2.0 ** zoom
	lon_deg = xtile / n * 360.0 - 180.0
	lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
	lat_deg = math.degrees(lat_rad)
	return (lat_deg, lon_deg)
	

#get the range of tiles that intersect with the bounding box of the polygon	
def getTileRange(polygon, zoom):
	bnds=polygon.bounds
	xm=bnds[0]
	xmx=bnds[2]
	ym=bnds[1]
	ymx=bnds[3]
	bottomRight=(xmx,ym)
	starting=deg2num(ymx,xm, zoom)
	ending=deg2num(ym,xmx, zoom) # this will be the tiles containing the ending
	x_range=(starting[0],ending[0])
	y_range=(starting[1],ending[1])
	return(x_range,y_range)

#to get the tile as a polygon object
def getTileASpolygon(z,y,x):
	nw=num2deg(x,y,z)
	se=num2deg(x+1, y+1, z)
	xm=nw[1]
	xmx=se[1]
	ym=se[0]
	ymx=nw[0]
	tile_bound=Polygon([(xm,ym),(xmx,ym),(xmx,ymx),(xm,ymx)])
	return tile_bound	
	
#to tell if the tile intersects with the given polygon	
def doesTileIntersects(z, y, x, polygon):
	if(z<10):	#Zoom tolerance; Below these zoom levels, only check if tile intersects with bounding box of polygon
		return True
	else:
		#get the four corners
		tile=getTileASpolygon(x,y,z)
		return polygon.intersects(tile)
		
#convert the URL to get URL of Tile		
def getURL(x,y,z,url):
	u=url.replace("{x}", str(x))
	u=u.replace("{y}", str(y))
	u=u.replace("{z}", str(z))
	return u

#this is your study Area. You need to change the extent here
#In this Example, I've given the boundary of Mumbai
	
stArea=Polygon([(72.7752778054935,19.2690995044639),(72.7817405956684,19.1238719055124),(72.8102749851638,19.1265959946878),(72.8247751057141,19.0910359643985),(72.8153720376396,19.0437583107182),(72.8209940779221,19.0352490234709),(72.8329105061117,19.0434886443927),(72.8359963318184,19.0373312064806),(72.8231900924928,19.0205055493087),(72.8125475128558,19.029908429424),(72.8080633067106,18.9898352623244),(72.7870845004595,18.947660113865),(72.7942309393155,18.937263881405),(72.809080960536,18.9503035811928),(72.8217391510222,18.9394947874404),(72.799135569344,18.9068306279723),(72.8113769649099,18.8893472433276),(72.8218126386322,18.8951870964281),(72.8474780411575,18.9235963464463),(72.8675088075429,19.0019646776918),(72.8819781251631,19.0064190047499),(72.8877097499884,18.9888559741936),(72.9236539940438,18.9983155390154),(72.9660988576404,19.0502455556637),(72.9836291475658,19.1747956918978),(72.9248922078066,19.2203564322991),(72.8998650805814,19.2558042171924),(72.8514714066599,19.2738226789422),(72.8514714066599,19.2738226789422),(72.8514714066599,19.2738226789422),(72.7752778054935,19.2690995044639)])	

print stArea.bounds

loc=r"D:\\Tiles\\MapQuestOpen_OSM" #You need to change the location for files to download
server_url=r"http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpeg" #This is the template for the Tile Sets


tileList=[]

for z in range(1, 17):
	ranges=getTileRange(stArea, z)
	x_range=ranges[0]
	y_range=ranges[1]
	
	for y in range(y_range[0], y_range[1]+1):
		for x in range(x_range[0], x_range[1]+1):
			if(doesTileIntersects(x,y,z,stArea)):
				tileList.append((z, y, x))
tileCount=len(tileList)


print 'Total number of Tiles: ' + str(tileCount)
count=0


# Now do the downloading
for t in tileList:
	#makeSure that folder exist; if not make it
	folderPath=os.path.join(loc,str(t[0]),str(t[2]))
	filePathJ=os.path.join(folderPath,str(t[1])+'.jpg')
	if (not os.path.exists(folderPath)):
		os.makedirs(folderPath)
	#make the URL
	url=getURL(t[2], t[1],t[0], server_url)
	print url
	
	urllib.urlretrieve(url,filePathJ)
	count=count+1
	print 'finished '+str(count)+'/'+str(tileCount)
