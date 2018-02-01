from draftsman import *

def f(x):
    return x

drawman_scale(25)
drawman_setka()
for x in range(-5,6):
    to_point(x,f(x))
    pen_down()
pen_up()
