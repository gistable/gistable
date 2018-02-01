# Color Temperature & Brightness calculations adapted from
#   https://github.com/KristopherKubicki/smartapp-circadian-daylight

# Sorry if this code sucks, I've never used Python before ;)


import logging
import datetime
import math

from homeassistant.components import light, sun
from homeassistant.util import dt as dt_util

DEPENDENCIES = ['sun', 'light']
DOMAIN = 'circadianlights'
SERVICE_CHANGE_ACTIVE_LIGHTS = 'change_lights'
CONF_LIGHTS = 'lights'
CONF_LIGHTS_TEMP = 'lights_temp'
CONF_BRIGHTNESS = 'lights'


def setup(hass, config):
    logger = logging.getLogger(__name__)

    def calculatecolor():
        sunrise = sun.next_rising(hass)
        sunset = sun.next_setting(hass)
        currenttime = dt_util.as_local(datetime.datetime.today())
        midday = sunrise + datetime.timedelta(seconds=(sunset - sunrise).total_seconds() / 2)
        brightness = 1
        colortemp = 2000

        if sunrise > sunset:
            if currenttime < midday:
                colortemp = 2000 + ((currenttime - sunrise) / (midday - sunrise) * 3800)
                brightness = ((currenttime - sunrise) / (midday - sunrise))
            else:
                colortemp = 6500 - ((currenttime - midday).total_seconds() / sunset.timestamp() * 3800)
                brightness = 1 - ((currenttime - midday).total_seconds() / sunset.timestamp())
        return ColorInfo(colortemp, max(brightness, 1))

    def getlights(key):
        light_ids = []
        for light_id in config[DOMAIN].get(key):
            if hass.states.get(light_id) is None:
                logger.error('Light id %s could not be found in state machine', light_id)
                return []
            if light.is_on(hass, light_id):
                light_ids.append(light_id)
        return light_ids

    def setlightcolor():
        color = calculatecolor()
        lights = getlights(CONF_LIGHTS)
        lights_with_temp = getlights(CONF_LIGHTS_TEMP)
        logger.info('Temperature: %s mireds, RGB: %s,%s,%s, Brightness: %s',
                    color.temperature, color.brightness,color.r,color.g,color.b)
        for light_id in lights:
            logger.info('setting light %s', light_id)
            light.turn_on(hass, light_id, transition=5,
                          rgb_color=[color.r, color.g, color.b], brightness=color.brightness)

        for light_id in lights_with_temp:
            logger.info('setting light %s', light_id)
            light.turn_on(hass, light_id, transition=5,
                          color_temp=color.temperature, brightness=color.brightness)

    hass.services.register(DOMAIN, SERVICE_CHANGE_ACTIVE_LIGHTS, lambda call: setlightcolor())
    return True


class ColorInfo:

    def __init__(self, tempkelvin, brightness):
        self.temperature = min(499, max(154, math.floor(1000000 / tempkelvin)))
        self.brightness = min(brightness * 255, 255)
        temp = tempkelvin / 100
        if temp < 10:
            temp = 10
        if temp > 400:
            temp = 400
        self.r = self.get_r_part(temp)
        self.g = self.get_g_part(temp)
        self.b = self.get_b_part(temp)

    @staticmethod
    def get_r_part(ct):
        if ct <= 66:
            r = 255
        else:
            r = 329.698727446 * ((ct - 60) ** -0.1332047592)
        if r < 0:
            r = 0
        if r > 255:
            r = 255
        return math.floor(r)

    @staticmethod
    def get_g_part(ct):
        if ct <= 66:
            g = 99.4708025861 * math.log(ct) - 161.1195681661
        else:
            g = 288.1221695283 * ((ct - 60) ** -0.0755148492)

        if g < 0:
            g = 0
        if g > 255:
            g = 255
        return math.floor(g)

    @staticmethod
    def get_b_part(ct):
        if ct >= 66:
            b = 255
        elif ct <= 19:
            b = 0

        else:
            b = 138.5177312231 * math.log(ct - 10) - 305.0447927307
        if b < 0:
            b = 0
        if b > 255:
            b = 255
        return math.floor(b)

