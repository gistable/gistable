# This is free and unencumbered software released into the public domain. See
# http://unlicense.org/

class PureEvil:
    def __init__(self):
        self.next_result = True

    def __bool__(self):
        self.next_result = (not self.next_result)
        return self.next_result