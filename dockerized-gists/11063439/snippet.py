import requests
from sets import Set 

_seed = 'http://apibunny.com/cells/taTKQ3Kn4KNnmwVI'
_base = 'http://apibunny.com/cells/'
visited = Set()

def processJson(json) : 
    cells = json.get('cells')[0]
        
    print cells["name"]
    links = cells['links']
    toVisit = [ _base + links[x] for x in  [k for k in links if k != "mazes"]]  
    map(visit, toVisit)
            

def visit(url):
    if url in visited :
        return
    document = requests.get(url)
    visited.add(url) 
    if document : 
        processJson(document.json());
            

if __name__ == "__main__":
    visit(_seed)
