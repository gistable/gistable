# Mini-project # 7 - Spaceship
#
# 'Introduction to Interactive Programming in Python' Course
# RICE University - coursera.org
# by Joe Warren, John Greiner, Stephen Wong, Scott Rixner

import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0


class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated


# art assets created by Kim Lathrop, may be freely re-used in
# non-commercial projects, please credit Kim

# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
# debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png,
# debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
missile_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png,
# explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")


# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# Sprite class
class Sprite():
    def __init__(self, pos, vel, angle, angle_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = angle
        self.angle_vel = angle_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        self.sound = sound
        if self.sound:
            self.sound.rewind()
            self.sound.play()

    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)

    def update(self, friction=0.0):
        # update orientation
        self.angle += self.angle_vel
        for i in range(2):
            self.vel[i] *= 1 - friction
        # update position
        limits = (WIDTH, HEIGHT)
        for i in range(2):
            self.pos[i] += self.vel[i]
            self.pos[i] = self.pos[i] % limits[i]


# Ship class, it inherits from Sprite class
class Ship(Sprite):
    def __init__(self, *args, **kwds):
        Sprite.__init__(self, *args, **kwds)  # inherit from sprite
        self.thrust = False
        if self.sound:
            self.sound.pause()
            self.sound.rewind()

    def set_thrust(self, value):
        self.thrust = value
        # shift image center and play/pause sound
        if value:
            self.image_center[0] *= 3
            if self.sound:
                self.sound.play()
        else:
            self.image_center[0] /= 3
            if self.sound:
                self.sound.pause()
                self.sound.rewind()

    def shoot(self):
        # shoot and return a missile (Sprite object)
        point_at = angle_to_vector(self.angle)
        pos = list(self.pos)
        vel = list(self.vel)
        for i in range(2):
            pos[i] += point_at[i] * self.image_center[0]
            vel[i] += point_at[i] * 5
        return Sprite(pos, vel, self.angle, 0, missile_image,
                      missile_info, missile_sound)

    def update(self):
        # move forward
        if self.thrust:
            vel = angle_to_vector(self.angle)
            for i in range(2):
                self.vel[i] += vel[i] * 0.2
        # sprite behaviour
        Sprite.update(self, 0.01)


# draw handler
def draw(canvas):
    global time
    # animate background
    time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(),
                      nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                      [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, [center[0] - wtime, center[1]],
                      [size[0] - 2 * wtime, size[1]],
                      [WIDTH / 2 + 1.25 * wtime, HEIGHT / 2],
                      [WIDTH - 2.5 * wtime, HEIGHT])

    # draw lives
    canvas.draw_text("Lives", (40, 40), 18, "White", "sans-serif")
    canvas.draw_text(str(lives), (40, 64), 18, "White", "sans-serif")

    # draw score
    canvas.draw_text("Score", (WIDTH - 80, 40), 18, "White", "sans-serif")
    canvas.draw_text(str(score), (WIDTH - 80, 64), 18, "White", "sans-serif")

    # draw ship and rocks
    my_ship.draw(canvas)
    a_rock.draw(canvas)

    # update ship and rocks
    my_ship.update()
    a_rock.update()

    # draw and update missiles
    for i in missiles:
        i.draw(canvas)
        i.update()


def key_down(key):
    global missiles
    if simplegui.KEY_MAP.get("up") == key:
        my_ship.set_thrust(True)
    elif simplegui.KEY_MAP.get("left") == key:
        my_ship.angle_vel = -0.1
    elif simplegui.KEY_MAP.get("right") == key:
        my_ship.angle_vel = 0.1
    elif simplegui.KEY_MAP.get("space") == key:
        missiles.append(my_ship.shoot())


def key_up(key):
    if simplegui.KEY_MAP.get("up") == key:
        my_ship.set_thrust(False)
    elif simplegui.KEY_MAP.get("left") == key:
        my_ship.angle_vel = 0.0
    elif simplegui.KEY_MAP.get("right") == key:
        my_ship.angle_vel = 0.0


# timer handler that spawns a rock
def rock_spawner():
    pos = [random.random() * WIDTH]
    pos.append(random.random() * HEIGHT)
    a_rock.pos = pos
    a_rock.vel = angle_to_vector(random.random() * 2 * 3.141592)  # random vel
    a_rock.angle_vel = (random.random() - 0.5) * 0.05  # random spin vel


# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, 0, ship_image, ship_info,
               ship_thrust_sound)
a_rock = Sprite([0, 0], [0, 0], 0, 0, asteroid_image, asteroid_info)
rock_spawner()  # force a initial spawn
missiles = list()

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
