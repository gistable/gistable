import rdflib

def links_generator(graph):
    for obj in g.objects():
        if "][|-|" in obj:
		    idx = obj.find("http", 0, len(obj))
		    idx2 = obj.rfind("%5D%5B0", 0, len(obj))
		    link = obj[idx:idx2]
		    yield link

if __name__ == "__main__":
	g = rdflib.Graph()
	g.parse("tabmix_sessions-2015-11-14.rdf") # replace with your own

	links = []
	for link in links_generator(g):
		links.append(link)

	print "Found", len(links), "links"

	with open("links.html", "w") as fp:
		fp.write("<html><body>")
		for link in links:
			fp.write("<a href=\""+link+"\">" + link + "</a><br>\r\n")
		fp.write("</body></html>")
