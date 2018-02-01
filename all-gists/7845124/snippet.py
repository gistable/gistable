import json
import urllib

class WazeLocationNotFoundException(Exception):
    pass

class Waze(object):
    _BASE_URL = "http://www.waze.co.il/"

    def __mozi(self, query):
        url = Waze._BASE_URL + "WAS/mozi"
        result = urllib.urlopen(url, data=urllib.urlencode({"q": query})).read()
        return json.loads(result)

    def locationOf(self, place):
        response = self.__mozi(place)
        if response:
            return response[0][u"location"]
        raise WazeLocationNotFoundException("'%s' cannot be found" % place)

    def __routeData(self, fromLocation, toLocation, maxNumberOfRoutes):
        url = Waze._BASE_URL + "RoutingManager/routingRequest"
        params = {
            "from": "x:%s y:%s bd:true" % (fromLocation[u"lon"], fromLocation[u"lat"]),
            "to": "x:%s y:%s bd:true" % (toLocation[u"lon"], toLocation[u"lat"]),
            "returnJSON": "true",
            "returnGeometries": "false",
            "returnInstructions": "false",
            "timeout": 60000,
            "nPaths": maxNumberOfRoutes
        }
        return json.loads(urllib.urlopen(url, data=urllib.urlencode(params)).read())

    def routes(self, source, target, maxNumberOfRoutes = 2):
        fromLocation = self.locationOf(source)
        toLocation = self.locationOf(target)

        result = self.__routeData(fromLocation, toLocation, maxNumberOfRoutes)
        
        routes = []
        for route in result[u"alternatives"]:
            directions = []
            for direction in route[u"response"][u"results"]:
                directions.append({
                    "crossTime": direction[u"crossTime"],
                    "crossTimeWithoutRealTime": direction[u"crossTimeWithoutRealTime"],
                    "distance": direction[u"distance"],
                    "length": direction[u"length"],
                })
            routes.append(directions)

        return routes

if __name__ == "__main__":
    waze = Waze()

    routes = waze.routes("Jerusalem", "Tel Aviv", 3)

    for index, route in enumerate(routes):
        print "Route %d" % index
        print "====================="
        print "Total length: %g km" % (sum([d["length"] for d in route]) / 1000.0)
        print "Total time: %g mins" % (sum([d["crossTime"] for d in route]) / 60.0)
        print "Total time (w/o real time): %g mins" % (sum([d["crossTimeWithoutRealTime"] for d in route]) / 60.0)
        print
