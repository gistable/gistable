import time, re
from selenium import selenium

class implicitWaitSelenium(selenium):
    """
    Extending the regular selenium class to add implicit waits
    """

    def __init__(self, *args):
        self.implicit_wait = 30
        super(implicitWaitSelenium, self).__init__(*args)

    def do_command(self, verb, args, implicit_wait=None):
        if implicit_wait is None:
            implicit_wait = self.implicit_wait

        try:
            return super(implicitWaitSelenium, self).do_command(verb, args)
        except Exception, e:
            if (re.match("ERROR: Element .* not found", str(e))
                and implicit_wait > 0):
                time.sleep(1)
                return self.do_command(verb, args, implicit_wait-1)
            raise Exception(e)
