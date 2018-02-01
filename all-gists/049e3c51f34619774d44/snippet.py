#let's say there are 1,234 pages to scrape in total
last_page = 1234

#And the page numbering starts at "1"
first_page = 1

#This is the way to scrape every record in a single process
def scrape_all_pages():
  scrape_page_range(first_page, last_page)

#This is how you could scrape every single record in parrallel - 
# use as many "number_of_processes" as you can afford 
# there will be diminishing returns at some point as you become memory, network, or (maybe but probably not) CPU bound
def scrape_in_parrallel(number_of_processes):
  total_number_of_pages = last_page - first_page + 1
  
  # don't lose anything to rounding! Check my math here, it's probably wrong.
  pages_per_process = ceiling(float(total_number_of_pages) / number_of_processes)
  
  for process in number_of_processes:
    is_child = os.fork()
    if is_child:
      starting_page = pages_per_process * process
      finishing_page = starting_page + pages_per_process #-1? maybe beware of off by one errror. Math is probably wrong again.
      scrape_page_range(starting_page, finishing_page)
    else: #in parent process
      print("forked child %s", prcocess)


def scrape_page_range(finishing_page):
  starting_page = 1
  for page in (starting_page..finishing_page):
    scrape_page(page)
    
# This is where you put all the logic specific to crawling a single "page" 
# or record or whatever fundamental "job" that you are trying to parrallelize, 
# given it's page_number
def scrape_page(page_number):
  print "scraping page %s", page
  
  #pretend this is work, using Beautiful soup or whatever.
  sleep(1); 
  
  # In reality, it would be something more like this.
  # url = "http://some_site.com?page=%s", page_number
  # request.get(url)
  
  if __name__ == '__main__':
    # Run the job in 12 different processes that split up the work more-or-less evenly 
    scrape_in_parrallel(12)
    
    