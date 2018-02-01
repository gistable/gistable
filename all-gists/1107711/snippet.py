class SeleniumTestCase(TestCase):

    # Let us just call self.click or self.type instead of self.selenium.type
    def __getattr__(self, name):
        if hasattr(self, 'selenium'):
            return getattr(self.selenium, name)
        raise AttributeError(name)
    
    # Ignore open commands that fail (same needs to be don for wait_for_page_to_load)
    def open(self, url, ignoreResponseCode=True):
        try:
            self.selenium.open(url, ignoreResponseCode)
        except Exception, e:
            print "Open failed on %s. Exception: %s" % (url, str(e))
            pass #sometimes open appears to work fine but flakes out. ignore those

    # Report pass/fail status to Sauce Labs
    def tearDown(self):
        passed = {'passed': self._exc_info() == (None, None, None)}
        self.set_context("sauce: job-info=%s" % json.dumps(passed))
        self.stop()
