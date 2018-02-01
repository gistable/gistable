from microbit import *
import random

MIN_X = 0
MAX_X = 4
MIN_Y = 0
MAX_Y = 4
EGG_START_Y = 0
BASKET_START_X = 2
BASKET_Y = 4

TICK = 1000

BASKET_BRIGHTNESS = 9
EGG_BRIGHTNESS = 3
OFF_BRIGHTNESS = 0


class Egg:
    def __init__(self, x):
        self.x = x
        self.y = EGG_START_Y

    def show(self):
        try:
            display.set_pixel(self.x, self.y, EGG_BRIGHTNESS)
        except ValueError:
            pass

    def hide(self):
        display.set_pixel(self.x, self.y, OFF_BRIGHTNESS)

    def move_down(self):
        self.y += 1

    def is_smashed(self):
        return (self.y > MAX_Y)

    def is_caught(self, x):
        return ((self.y == MAX_Y) and (self.x == x))


class Basket:
    x = BASKET_START_X

    def set_x(self, x):
        self.x = x

    def get_x(self):
        return self.x

    def hide(self):
        display.set_pixel(self.x, BASKET_Y, OFF_BRIGHTNESS)

    def show(self):
        display.set_pixel(self.x, BASKET_Y, BASKET_BRIGHTNESS)


basket = Basket()

eggs = []


def hide_eggs():
    for egg in eggs:
        egg.hide()


def show_eggs():
    for egg in eggs:
        egg.show()


def move_eggs():
    for egg in eggs:
        egg.move_down()


def caught_egg():
    return ([egg for egg in eggs if egg.is_caught(basket.get_x())])


def sweep_up_eggs():
    eggs[:] = [egg for egg in eggs if (not egg.is_smashed() and not egg.is_caught(basket.get_x()))]


def move_basket():
    current_x = basket.get_x()
    if button_a.was_pressed():
        # move left
        if current_x > MIN_X:
            basket.hide()
            basket.set_x(current_x - 1)
    elif button_b.was_pressed():
        # move right
        if current_x < MAX_X:
            basket.hide()
            basket.set_x(current_x + 1)
    basket.show()


def start_game():
    global last_tick
    global score
    last_tick = running_time()
    score = 0
    eggs.append(Egg(0))
    eggs.append(Egg(3))
    show_eggs()
    basket.show()


def finish_game():
    display.scroll(str(score))


def add_new_egg():
    eggs.append(Egg(random.randint(0, 4)))


def play_game():
    global last_tick
    global score
    while not accelerometer.was_gesture("face down"):
        move_basket()
        if running_time() - last_tick > TICK:
            last_tick += TICK
            hide_eggs()
            move_eggs()
            if caught_egg():
                score += 1
            add_new_egg()
            sweep_up_eggs()
            show_eggs()


# Main program

start_game()
play_game()
finish_game()
