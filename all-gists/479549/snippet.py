class QuickOutputter(object):
    def __lt__(self, msg):
        print msg
        return self

o = QuickOutputter()
o < "Some random message"
o < "Some other message"
