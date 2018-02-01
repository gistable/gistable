from wemos import *
from machine import Pin, PWM
import machine
import time
import urequests
import urandom

red = PWM(Pin(D8), freq=512, duty=0)
green = PWM(Pin(D7), freq=512, duty=0)
blue = PWM(Pin(D6), freq=512, duty=0)
button = Pin(D5, Pin.IN)



def urandint(mi, ma=None, bits=10):
    if ma is None:
        mi, ma = 0, mi
    return int(mi + (urandom.getrandbits(bits) / 2**bits )*(ma-mi))

def clean_leds():
    for led in [red, green, blue]:
        led.freq(512)
        led.duty(0)
    
def loop():
    check_weather = False
    def callback(_):
        nonlocal check_weather
        check_weather = True
        
    button.irq(trigger=Pin.IRQ_RISING, handler=callback)
    while True:        
        if check_weather:
            weather = urequests.get("http://api.openweathermap.org/data/2.5/weather?q=<CITYNAME>&APPID=<APIKEY>&units=metric").json()
            status = weather["weather"][0]["main"]
            func = getattr(Effects, status.lower())
            clean_leds()
            func()
            clean_leds()
            check_weather = False
        time.sleep(3)     
       
class Effects:
    @staticmethod
    def thunderstorm():
        for i in range(urandint(2, 4)):  # foreshock
            blue.duty(urandint(200, 400))
            time.sleep(0.2)
            blue.duty(urandint(0, 200))
            time.sleep(0.2)    
        blue.duty(urandint(600, 1024))  # strong lightning
        time.sleep(0.4)
        blue.duty(urandint(0, 200))
        time.sleep(0.2)
        blue.duty(urandint(400, 800))  # weak lightning
        time.sleep(0.4)
        blue.duty(urandint(0, 200))
        time.sleep(0.2)
        for i in range(urandint(4, 8)):  # aftershock
            blue.duty(urandint(200, 400))
            time.sleep(0.1)
            blue.duty(urandint(0, 200))
            time.sleep(0.1)

    @staticmethod
    def drizzle():
        for i in range(20):
            blue.duty(urandint(0, 400))  # mo drizzle
            green.duty(urandint(0, 400))  # fo shizzle
            time.sleep(urandint(50, 500)/1000)  # to nizzle

    @staticmethod
    def rain():
        for i in range(40):
            blue.duty(urandint(200, 800))  # even mo drizzle
            green.duty(urandint(200, 800))  # fo shizzle
            time.sleep(urandint(50, 100)/1000)  # no nizzle

    @staticmethod
    def snow():
        res = 16
        for i in range(10):
            effect = urandom.getrandbits(2)
            if effect == 0:
                for j in range(urandint(0, 400) / res):
                    blue.duty(600 + (j*res))
                    time.sleep(0.1)
            elif effect == 1:
                for j in range(urandint(0, 600) / res):
                    blue.duty(800 - (j*res))
                    time.sleep(0.1)
            elif effect == 2:
                for j in range(urandint(0, 600) / res):
                    blue.duty(300 + (j*res))
                    time.sleep(0.1)
            elif effect == 3:
                for j in range(urandint(0, 800) / res):
                    blue.duty(200+(j*res))
                    time.sleep(0.1)
                for j in range(urandint(0, 600) / res):
                    blue.duty(1024-(j*res))
                    time.sleep(0.1)

    @staticmethod
    def atmosphere():
        res = 16
        for i in range(10):
            for j in range(urandint(0, 200) / res):
                green.duty(200 + (j*res))
                red.duty(200 + (j*res))
                time.sleep(0.1)
            for j in range(urandint(0, 200) / res):
                green.duty(200-(j*res))
                red.duty(200-(j*res))
                time.sleep(0.1)

    @staticmethod
    def clear():
        res = 16
        for i in range(10):
            effect = urandom.getrandbits(2)
            for j in range(urandint(0, 200) / res):
                if effect == 0:
                    green.duty(800 + (j*res))
                else:
                    red.duty(800 + (j*res))
                time.sleep(0.1)
            for j in range(urandint(0, 200) / res):
                if effect == 1:
                    green.duty(1024-(j*res))
                else:
                    red.duty(1024-(j*res))
                time.sleep(0.1)

    @staticmethod
    def clouds():
        res = 16
        for i in range(10):
            effect = urandom.getrandbits(2)
            if effect == 0:
                for j in range(urandint(0, 400) / res):
                    red.duty(600 + (j*res))
                    time.sleep(0.1)
            elif effect == 1:
                for j in range(urandint(0, 600) / res):
                    green.duty(800 - (j*res))
                    time.sleep(0.1)
            elif effect == 2:
                for j in range(urandint(0, 600) / res):
                    red.duty(300 + (j*res))
                    time.sleep(0.1)
            elif effect == 3:
                for j in range(urandint(0, 800) / res):
                    green.duty(200 + (j*res))
                    red.duty(200 + (j*res))
                    time.sleep(0.1)
                for j in range(urandint(0, 600) / res):
                    green.duty(1024-(j*res))
                    red.duty(1024-(j*res))
                    time.sleep(0.1)

    @staticmethod
    def extreme():
        for i in range(10):
            red.duty(1024)
            green.duty(1024)
            blue.duty(1024)
            time.sleep(0.3)
            red.duty(0)
            green.duty(0)
            blue.duty(0)
            time.sleep(0.3)

    addinational = extreme