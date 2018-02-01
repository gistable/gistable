from selenium import webdriver

profile = webdriver.FirefoxProfile()
# Set proxy settings to manual
profile.set_preference('network.proxy.type', 1)
# Set proxy to Tor client on localhost
profile.set_preference('network.proxy.socks', '127.0.0.1')
profile.set_preference('network.proxy.socks_port', 9050)
# Disable all images from loading, speeds page loading
# http://kb.mozillazine.org/Permissions.default.image
profile.set_preference('permissions.default.image', 2)
# Set all new windows to open in the current window instead
profile.set_preference('browser.link.open_newwindow', 1)
browser = webdriver.Firefox(profile)
browser.get('http://www.google.com/')
html = browser.page_source
