# -*- coding: utf-8 -*-
"""
Función que nos permite calcular la distancia entre 2 geo puntos
"""
import math

# Punto 1
lat1 = 20.694462
lon1 = -102.656250

# Point 2
lat2 = 31.742183
lon2 = -115.839844


def calculate_distance(lat1, lon1, lat2, lon2):
    if ((lat1 == lat2) and (lon1 == lon2)):
        return 0
    try:
        delta = lon2 - lon1
        a = math.radians(lat1)
        b = math.radians(lat2)
        C = math.radians(delta)
        x = math.sin(a) * math.sin(b) + math.cos(a) * math.cos(b) * math.cos(C)
        distance = math.acos(x) # in radians
        distance  = math.degrees(distance) # in degrees
        distance  = distance * 60 # 60 nautical miles / lat degree
        distance = (distance * 1852) / 1000 # conversion to KM's
        distance  = round(distance)
        return distance;
    except:
        return 0

distance = calculate_distance(lat1,lon1,lat1,lon2)
print "La distancia es: {0} Kms".format(distance)