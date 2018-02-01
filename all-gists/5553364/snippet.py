# Mini-project #2 - "Guess the number"
#
# 'Introduction to Interactive Programming in Python' Course
# RICE University - coursera.org
# by Joe Warren, John Greiner, Stephen Wong, Scott Rixner

import simplegui
import random

# initialize global variables used in your code
max_range = 100
guesses = int()  # placeholder, look at init()
message = dict()  # placeholder, look at init()
old_message = dict()  # placeholder, look at init()
random_number = int()  # placeholder, look at init()
max_guesses = int()  # placeholder, look at init()

# canvas constants
FONT_SIZE = 14
CANVAS_WIDTH = 420
CANVAS_HEIGHT = 180
AVATAR_SIZE = 40
MARGIN = 6
AVATAR_COORD = {"player": AVATAR_SIZE // 2 + MARGIN,
                "python": CANVAS_WIDTH - MARGIN - AVATAR_SIZE // 2}
BUBBLE_MARGIN = {"player": (AVATAR_SIZE + (2 * MARGIN), CANVAS_WIDTH - MARGIN),
                 "python": (MARGIN, CANVAS_WIDTH - (2 * MARGIN) - AVATAR_SIZE)}
AVATAR = {"python": simplegui.load_image("http://goo.gl/DZjuc"),
          "player": simplegui.load_image("http://goo.gl/4fJNf")}

# canvas animation constants
time = 0  # global time
TRANSITION = 5  # transition duration


# helper functions
def init():
    global old_message, message, random_number, guesses, max_guesses
    # restart number of guesses
    guesses = 0
    # set max number of guesses
    if max_range == 100:
        max_guesses = 7
    else:
        max_guesses = 10
    # get random number
    random_number = random.randint(0, max_range - 1)
    # message is a dictionary holding the logging messages,
    # keys represent the player name and values the messages.
    # Values are stored in a list because canvas.draw_text()
    # can't handle multiline strings automatically.
    message = {"python": ["Do you wanna play 'guess the number'?",
                          "I am thinking of a number between 0 and %s (inclusive)." % str(max_range - 1),
                          "Take a guess!"],
               "player": list()}
    old_message = message  # buffer for transition
    print "\n--- NEW GAME ---"
    log_to_console()


def log_to_console():
    # Log message dict to the console
    for player in ("player", "python"):
        for text in message.get(player):
            print "%s: %s" % (player, text)


# define event handlers for control panel
def tick():
    # simple timer, this is necessary to animate transitions
    # between sessions on the canvas.
    global time
    time += 1


def range100():
    # button that changes range to range [0,100) and restarts
    global max_range
    max_range = 100
    init()


def range1000():
    # button that changes range to range [0,1000) and restarts
    global max_range
    max_range = 1000
    init()


def get_input(guess):
    global message, guesses, time
    # assign your guess to the player message
    message["player"] = [guess]
    # validate
    if not guess or not (0 <= int(guess) < max_range):
        message["python"] = ["Pick a number between 0 and %s, try again..." % str(max_range - 1)]
        log_to_console()
        time = 0  # restart time
        timer.start()  # start transition
        return
    # count guesses
    guess = int(guess)
    guesses += 1
    # check for a new game
    if max_guesses - guesses < 0:
        return init()
    # check for a winner
    elif guess == random_number:
        message["python"] = ["Good job!",
                             "You guessed my number in %s guesses :)" % guesses,
                             "",
                             "Do you wanna play again?"]
        guesses = 8  # start a new game
    # check for game over
    elif max_guesses - guesses == 0:
        message["python"] = ["Oops!! No turns left :(",
                             "My number was %s..." % random_number,
                             "",
                             "Do you wanna play again?"]
        guesses = 8  # start a new game
    # keep playing
    else:
        comp_guess = "high"
        if guess < random_number:
            comp_guess = "low"
        message["python"] = ["Your guess is too %s!" % comp_guess,
                             "You have %s turns left." % str(max_guesses - guesses),
                             "Try again..."]
    log_to_console()
    time = 0  # retart timeline
    timer.start()  # start transition


def draw(canvas):
    # optional event handler, this function draws a chat/log window
    # showing the last interaction between the user and the system
    # directly into the canvas.
    next_page = False
    for text in (old_message, message):
        base_height = 0  # base y coordinate for each message group
        for player in ("player", "python"):
            message_length = len(message.get(player))
            if not message_length:
                continue  # if there's no message for this player, skip this iteration
            offset = (CANVAS_HEIGHT * time / TRANSITION)  # y coord offset for next page
            # render avatar
            avatar_posy = (AVATAR_SIZE // 2) + MARGIN + base_height - offset
            if next_page:
                avatar_posy += CANVAS_HEIGHT
            canvas.draw_image(AVATAR.get(player),
                             (40, 40), (80, 80),
                             (AVATAR_COORD.get(player), avatar_posy),
                             (AVATAR_SIZE, AVATAR_SIZE))
            # render bubble
            bubble_height = (message_length * FONT_SIZE) + ((message_length + 1) * MARGIN)
            bubble_posy = [MARGIN + base_height - offset,
                           bubble_height + base_height - offset]
            if next_page:
                bubble_posy[0] = bubble_posy[0] + CANVAS_HEIGHT
                bubble_posy[1] = bubble_posy[1] + CANVAS_HEIGHT
            canvas.draw_polygon([(BUBBLE_MARGIN.get(player)[0], bubble_posy[0]),
                                 (BUBBLE_MARGIN.get(player)[0], bubble_posy[1]),
                                 (BUBBLE_MARGIN.get(player)[1], bubble_posy[1]),
                                 (BUBBLE_MARGIN.get(player)[1], bubble_posy[0])],
                                1, "Silver", "White")
            # render text
            i = 0  # line number
            for text in message.get(player):
                text_posy = (1 + i) * (MARGIN + FONT_SIZE) + base_height - offset
                if next_page:
                    text_posy += CANVAS_HEIGHT
                canvas.draw_text(text, (BUBBLE_MARGIN.get(player)[0] + 2,
                                 text_posy),
                                 FONT_SIZE, "Black", "sans-serif")
                i += 1  # acumulate line number
            # acumulate y coordinate to use it in the next message group
            if bubble_height > AVATAR_SIZE:
                base_height += bubble_height
            else:
                base_height += AVATAR_SIZE + MARGIN
            # change to next page offset
            next_page = True
    if time >= TRANSITION:
        timer.stop()

# create frame
frame = simplegui.create_frame("Guess the number", CANVAS_WIDTH, CANVAS_HEIGHT)
frame.set_canvas_background("Gray")

# register event handlers for control elements
frame.add_button("Range is [0-100)", range100, 200)
frame.add_button("Range is [0-1000)", range1000, 200)
frame.add_input("Enter a guess:", get_input, 195)
frame.set_draw_handler(draw)  # canvas handler, used to draw stuff on the canvas
timer = simplegui.create_timer(1000//30, tick)  # timer handler, used by transitions

# start frame
init()
frame.start()
