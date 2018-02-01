# After spending too much time away from Python on Javascript, I gave this a shot. To my surprise, it worked!
# Since Python doesn't bind "self" implicitly in classes, this looks pretty similar to Python classes.
# You want inheritance? Pass in the Parent "class" and copy the key/vals a la Javascript.
# Even adding dot syntax is not too tough.

def Cat(legs, colorId, name):
    def sayHi():
        print 'Hi, my name is %s. I have %s legs and am %s.' % (this['name'], this['legs'], this['color'])

    this = {
        'legs': legs,
        'color': ['black', 'brown'][colorId],
        'name': name,
        'sayHi': sayHi
    }
    return this

myCat = Cat(4, 0, 'Joey')
hisCat = Cat(3, 1, 'Bill')

myCat['sayHi']() # Joey
hisCat['sayHi']() # Bill