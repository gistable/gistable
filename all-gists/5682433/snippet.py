import math

def distance(lat1, long1, lat2, long2):
  R = 6371 # Earth Radius in Km
	dLat = math.radians(lat2 - lat1) # Convert Degrees 2 Radians
	dLong = math.radians(long2 - long1)
	lat1 = math.radians(lat1)
	lat2 = math.radians(lat2)
	a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLong/2) * math.sin(dLong/2) * math.cos(lat1) * math.cos(lat2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = R * c
	return d