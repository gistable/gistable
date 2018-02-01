import re, urllib2
 
site = 'dont ask me ill never tell'
 
start = '/web/20090130021320/' + site + '/'
base = 'http://web.archive.org'
dest_folder = '/Users/jyan/Desktop/OMG'
 
keep_substr = '/' + site + '/uploads/'
 
url_pattern = re.compile(r"(/web/[^\s]+?/" + site + "/[^\s]*?)[\"'#]")
 
def find_urls(markup):
  return set(url_pattern.findall(markup))
 
def fetch_url(url):
  reader = urllib2.urlopen(url)
  markup = reader.read()
  reader.close()
  return markup
  
def save_file(url, data):
  name = url.split(keep_substr)[1]
  f = open(dest_folder + '/' + name, "w")
  f.write(data)
  f.close()
  print "\tSuccess saving %s into %s" % (url, name)
  
def unique_key(url):
  return url.split(site)[1]
  
def fetch_graph(start):
  stack = [start]
  added = set()  
  while len(stack) > 0:
    next = stack.pop()
    added.add(unique_key(next))
    
    print "Processing %s... (%d URLs)" % (next, len(added))
    
    try:
      data = fetch_url(base + next)
      
      print "Fetched %s: %d bytes" % (base + next, len(data))
      
      if next.find(keep_substr) >= 0:
        # download this guy instead
        save_file(next, data)
        
      else:  
        urls = find_urls(data)
 
        print "\tFound %d URLs" % (len(urls))
        
        for url in urls:
          if unique_key(url) not in added:
            stack.append(url)
    
    except Exception:
      print "\tFailed to fetch URL"
 
if __name__ == "__main__":
  print "Starting"
  fetch_graph(start)
  print "Done"