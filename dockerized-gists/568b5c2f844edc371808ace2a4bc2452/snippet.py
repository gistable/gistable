import requests

api_key = "ADD YOUR OWN API KEY"


def get_duration(source, destination, key):
    query_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    try:
        data = requests.get(query_url, params={
            "destinations": destination,
            "origins": source,
            "key": key,
            "units":"imperial"
        }).json()
        duration = data["rows"][0]["elements"][0]["duration"]["text"]
        return duration
    except KeyError as e:
        print("Key {} not available".format(e))

origin = input("Origin: ").split()
destination = input("Destination: ").split()
origins = "+".join(origin)
destinations = "+".join(destination)

print(get_duration(origins, destinations, api_key))
    