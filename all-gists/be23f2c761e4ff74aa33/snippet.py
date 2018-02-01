import requests

url = "http://www.bbc.co.uk/programmes/music/artists/charts.json"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    for artist in data["artists_chart"]["artists"]:
        print(artist)
else:
    print("Error: status_code", response.status_code)
