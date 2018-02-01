#first
if browser.lower() == 'firefox':
  driver = webdriver.Firefox
  self._kwargs.update({'browser_profile' if self._use_grid else 'firefox_profile': firefox_profile()})
  desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
            
#later
if self._use_grid:
  host = get_config().getini("grid_host")
  port = get_config().getini("grid_port")
  self._kwargs.update({'command_executor': 'http://{}:{}/wd/hub'.format(host, port), 'desired_capabilities': desired_capabilities})
  driver = webdriver.Remote

return driver

#finally
self._driver = self._driver(**self._kwargs)

#profile
def firefox_profile():
  from selenium import webdriver
  profile = webdriver.FirefoxProfile()
  profile.set_preference('browser.cache.check_doc_frequency', 1)
  profile.set_preference('startup.homepage_welcome_url.additional', 'about:blank')
  return profile