import json, urllib2, sys, math
import networkx as nx

def grab_files(url="http://fx.priceonomics.com/v1/rates/"):
    try:
        x = urllib2.urlopen(url).read()
        res = json.loads(x)
    except Exception, e:
        print >>sys.stderr, "Error getting rates:", e
        sys.exit(1)
    return res

def parse_point(t):
    tn = t[0].split("_")
    return (tn[0], tn[1], -1.0 * math.log(float(t[1])))

def build_graph(parsed_points):
    dg = nx.DiGraph()
    dg.add_weighted_edges_from(parsed_points)
    return dg

def find_path(digraph, start="USD"):
    path = nx.bellman_ford(digraph, start, return_negative_cycle=True)
    return path

def output_path(path, g, start="USD"):
    visited = set(start)
    tot=1.0
    pred = path[start]
    x = start
    while pred not in visited:
        print pred, "-->", x, math.exp(-g[pred][x]['weight'])
        tot*=math.exp(-g[pred][x]['weight'])
        visited.add(pred)
        x = pred
        pred = path[pred]
    
    tot *= math.exp(-g[start][x]['weight'])
    print start, "-->", x, math.exp(-g[start][x]['weight'])
    print "Total:", tot
    if tot < 1.0:
        print "Note: no arbitrage opportunity detected."

def main():
    obj = grab_files()
    parsed_points = map(parse_point, obj.items())
    dg = build_graph(parsed_points)
    path = find_path(dg)
    output_path(path, dg)

if __name__ == "__main__":
  main()