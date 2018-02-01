import re, mechanize, os, urllib

br = mechanize.Browser()
br.open("http://www.reddit.com/r/Cinemagraphs")

image = urllib.URLopener()
links = set()
i = 0;

dirname = "gifs"
if not os.path.isdir("./" + dirname + "/"):
   os.mkdir("./" + dirname + "/")

while True:
   
   for link in (br.links(url_regex=r"gif$")):
	   links.add(link.absolute_url)   

   for l in links:
         print str(i) + ". " + l
         try:
            m = re.search(r"[a-zA-Z0-9]*\.gif", l)
            if m:
               image.retrieve(l, "./" + dirname + "/" + m.group(0))
            else:
               image.retrieve(l, "./" + dirname + "/" + str(i) + ".gif")
         except Exception, e:
            print "Error retrieving gif from " + l
         i = i + 1
   links.clear()
   
   try:
      br.follow_link(url_regex=r"count=[0-9]*&after")
   except Exception, e:
      print "Error retrieving next reddit page due to api restrictions. Try again."
      exit(0)