    def tearDown(self):
        passed = {'passed': self._exc_info() == (None, None, None)}
        self.selenium.set_context("sauce: job-info=%s" % json.dumps(passed))
        self.selenium.stop()
