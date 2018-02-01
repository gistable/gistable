spider_count = 0

# Get a signal that a crawler has finished its job, start another crawler
def spider_closed(spider, reason):
    spider_count += 1

    #Only starts another crawler if available
    if spider_count < len(spiders):
        reactor.callLater(0, start_crawler, spider=spiders[spider_count])
    else:
        reactor.stop() #Stops reactor to prevent script from hanging
        

def start_crawler(spider):
    crawler = Crawler(get_project_settings()) #Loads the settings
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()

if __name__ == '__main__':
    
    # Subscribe to the "spider_closed" signals
    dispatcher.connect(spider_closed, signal=signals.spider_closed)
    
    spiders.append(Spider1())
    spiders.append(Spider2())
    
    reactor.callLater(0, start_crawler, spider=spiders[spider_count])
    
    reactor.installResolver(CachingThreadedResolver(reactor))
    
    #Start log and twisted reactor
    log.start()
    reactor.run(installSignalHandlers=False)