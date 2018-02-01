from threading import Thread
from selenium import webdriver
import time

API_KEY = "key"
API_SECRET = "secret"

def get_browser(caps):
    return webdriver.Remote(  
            desired_capabilities=caps,  
            command_executor="http://%s:%s@hub.testingbot.com:4444/wd/hub" % (API_KEY, API_SECRET)
        )

browsers = [
  { "platform":"WINDOWS", "browserName" : "firefox", "version" : 13, "name" : "FF13" }, 
  { "platform":"WINDOWS", "browserName" : "firefox", "version" : 14, "name" : "FF14" },
  { "platform":"LINUX", "browserName" : "chrome", "name" : "Chrome" },
  { "platform":"MAC", "browserName" : "safari", "version" : 6, "name" : "Safari6" }
]
browsers_waiting = []

def get_browser_and_wait(browser_data):
    print "starting %s" % browser_data["name"]
    browser = get_browser(browser_data)
    browser.get("http://testingbot.com")
    browsers_waiting.append({ "data" : browser_data, "driver" : browser })
    print "%s ready" % browser_data["name"]
    while len(browsers_waiting) < len(browsers):
        print "browser %s sending heartbeat while waiting" % browser_data["name"]
        browser.get("http://testingbot.com")
        time.sleep(3)

thread_list = []
for i, browser in enumerate(browsers):
    t = Thread(target=get_browser_and_wait, args=[browser])
    thread_list.append(t)
    t.start()

for t in thread_list:
    t.join()

print "all browsers ready"
for i, b in enumerate(browsers_waiting):
    print "browser %s's title: %s" % (b["data"]["name"], b["driver"].title)
    b["driver"].quit()
