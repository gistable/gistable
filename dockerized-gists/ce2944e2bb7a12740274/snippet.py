import mechanize
import cookielib
import selenium.webdriver

# Create a selenium instance for browsing web pages
driver = selenium.webdriver.Firefox()

# ... Perform some actions

# Grab the cookie
cookie = driver.get_cookies()

# Store it in the cookie jar
cj = cookielib.LWPCookieJar()

for s_cookie in cookie:
    cj.set_cookie(cookielib.Cookie(version=0, name=s_cookie['name'], value=s_cookie['value'], port='80', port_specified=False, domain=s_cookie['domain'], domain_specified=True, domain_initial_dot=False, path=s_cookie['path'], path_specified=True, secure=s_cookie['secure'], expires=s_cookie['expiry'], discard=False, comment=None, comment_url=None, rest=None, rfc2109=False))

# Instantiate a Browser and set the cookies
br = mechanize.Browser()
br.set_cookiejar(cj)

# Now open the URL:
br.open(url)