import requests, appex
from urllib.parse import urlparse
url = appex.get_url().replace("dl=0", "dl=1")
r = requests.get(url)
filename = urlparse(url).path.rpartition("/")[-1].replace(".py", "-downloaded.py")
with open(filename, "wb") as outfile:
    outfile.write(r.content)
print("script downloaded as " + filename)
