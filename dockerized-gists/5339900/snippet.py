# meta_troll.py
# This is me messing around with Python type constructors just for fun.
# Try and see what happens if you uncomment the __metaclass__ line in Foo.

class TrollType(type):
    def __new__(meta, classname, bases, clssDict):
        class MyTroll(object):
            def say_stuff(self):
                print("you mad bro?")
        return MyTroll


class Foo(object):
    #__metaclass__ = TrollType

    def say_stuff(self):
        print("hi there buddy!")

if __name__ == '__main__':
    f = Foo()
    f.say_stuff()
