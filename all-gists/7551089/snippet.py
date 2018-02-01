# Script: webpage_getlinks.py 
# Desc: Basic web site info gathering and analysis script. From a URL gets 
# page content, parsing links out. 
# 
import sys, re 
import webpage_get 
 
def print_links(page): 
 ''' find all hyperlinks on a webpage passed in as input and 
print ''' 
 print '[*] print_links()' 
 # regex to match on hyperlinks, returning 3 grps, links[1] being the link itself
 # The regex below is incorrect so don't take this as a final answer
 links = re.findall(r'(\<a.*href\=.*)(http\:.+)(\"+)', page) 
 # sort and print the links 
 links.sort() 
 print '[+]', str(len(links)), 'HyperLinks Found:' 
 for link in links: 
     print link
 
def main(): 
 # temp testing url argument 
 sys.argv.append('http://www.napier.ac.uk/Pages/home.aspx') 
 
 # Check args 
 if len(sys.argv) != 2: 
     print '[-] Usage: webpage_getlinks URL' 
     return 
 
 # Get the web page 
 page = webpage_get.wget(sys.argv[1]) 
 # Get the links 
 print_links(page) 
 
if __name__ == '__main__': 
 main()
