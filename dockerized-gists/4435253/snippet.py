# Get a next task from some tasks queue, create and start a crawler
def start_crawler():
    settings = CrawlerSettings()
    settings.overrides['TELNETCONSOLE_ENABLED'] = 0
    settings.overrides['WEBSERVICE_ENABLED'] = False

    crawler = Crawler(settings)
    crawler.configure()
    
    url = get_url_from_some_queue()
    
    crawler.crawl(SomeSpider(url))
      
    crawler.start()

# Get a signal that a crawler has finished its job, start another crawler
def spider_closed(spider, reason): 
    reactor.callLater(0, start_crawler)
 
def main():
  
    # Subscribe to the "spider_closed" signals
    dispatcher.connect(spider_closed, signals.spider_closed)
 
    # Start a required number of concurrent crawlers
    for i in range(number_of_concurrent_crawlers):
        reactor.callLater(0, start_crawler)
 
    reactor.installResolver(CachingThreadedResolver(reactor))
    
    # Run twisted reactor. This call is blocking.
    reactor.run(installSignalHandlers=False)
 
if __name__ == "__main__":
    main()