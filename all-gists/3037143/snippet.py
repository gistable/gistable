def UNIX_newlines(s):
    return s.replace('\n\r', '\n')

class UNIXPrinter(Printer):

    def printer(self):
        return UNIX_newlines(self.text)

p = UNIXPrinter('\n\r')
assert p.printer() == '\n'