
class Base(object):

    def __init__(self, arg):

        self.arg = arg


class BaseL(object):

    def __init__(self, arg):

        super(BaseL, self).__init__(arg)


class BaseR(object):

    def __init__(self, arg1, arg2):

        super(BaseR, self).__init__(arg1)



class LR(object):

    def __init__(self):

        super(LR, self).__init__(10)


if __name__ == '__main__':

    o = LR()
