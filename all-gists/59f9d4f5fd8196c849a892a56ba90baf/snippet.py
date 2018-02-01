"""
Support for Denon AVR Receivers.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.denonavr/
"""
import logging
from datetime import timedelta
import voluptuous as vol

from homeassistant.components.media_player import (
    MEDIA_TYPE_MUSIC, MEDIA_TYPE_CHANNEL, SUPPORT_TURN_OFF, SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET,SUPPORT_PAUSE, SUPPORT_PREVIOUS_TRACK, SUPPORT_NEXT_TRACK,
    SUPPORT_SELECT_SOURCE, MediaPlayerDevice, PLATFORM_SCHEMA)
from homeassistant.const import (STATE_OFF, STATE_ON, CONF_HOST, CONF_NAME)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)



PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
})

DENON_PLAYER_SUPPORT = SUPPORT_PAUSE | SUPPORT_NEXT_TRACK | SUPPORT_PREVIOUS_TRACK | \
	SUPPORT_SELECT_SOURCE | SUPPORT_TURN_OFF | SUPPORT_TURN_ON | SUPPORT_VOLUME_MUTE | \
	SUPPORT_VOLUME_SET

REQUIREMENTS = [
                'https://github.com/subutux/denonavr/archive/'
                '04c7789b1e4aad4b792b092ded87133df3c2dd47.zip'
                '#denonavr==0.5b4']

def setup_platform(hass, config, add_devices, discovery_info=None):
	from denonavr import denon
	myDenon = denon.Connect(config.get(CONF_HOST))
	add_devices([
		DenonDevice(myDenon)
		])

class DenonDevice(MediaPlayerDevice):
	def __init__(self,myDenon):
		self.denon = myDenon

	def update(self):
		self.denon.updateStatus()
		self.denon.updateInputs()
	@property
	def should_poll(self):
		return True
	
	@property
	def state(self):
		if self.denon.state == "ON":
			return STATE_ON
		elif self.denon.state == "STANDBY":
			return STATE_OFF
	@property
	def name(self):
		return self.denon.name

	@property
	def volume_level(self):
		return round(self.denon.volume_percent / 100)
	
	@property
	def is_volume_muted(self):
		return self.denon.mute
	
	@property
	def source_list(self):
		return list(self.denon.inputs)

	@property
	def source(self):
		return self.denon.input
	
	def select_source(self,source):
		self.denon.setInput(source)
		self.update_ha_state()

	def turn_on(self):
		self.denon.turnOn()
		self.update_ha_state()
	
	def turn_off(self):
		self.denon.turnOff()
		self.update_ha_state()

	def media_play(self):
		self.denon.play()
		self.update_ha_state()

	def media_pause(self):
		self.denon.pause()
		self.update_ha_state()

	def media_next_track(self):
		self.denon.next_track()
	
	def media_previous_track(self):
		self.denon.previous_track()

	def mute_volume(self,mute):
		self.denon.mute = mute

	def set_volume_level(self,level):
		self.denon.volume = level * 100
		self.update_ha_state()

	def volume_up(self):
		self.denon.volume_up()
	
	def volume_down(self):
		self.denon.volume_down()
	@property
	def media_content_type(self):
		if self.denon.nowPlaying["SONG"] == None:
			return MEDIA_TYPE_CHANNEL
		else:
			return MEDIA_TYPE_MUSIC
	@property
	def media_image_url(self):
		return self.denon.nowPlaying["ALBUM_ART"]
	@property
	def supported_media_commands(self):
		return DENON_PLAYER_SUPPORT
	@property
	def media_title(self):
		if self.denon.nowPlaying["SONG"] == None:
			return self.denon.nowPlaying["INPUT"]
		else:
			return self.denon.nowPlaying["ARTIST"] + ": " + self.denon.nowPlaying["SONG"]
	@property
	def media_artist(self):
		return self.denon.nowPlaying["SONG"]
	@property
	def media_album_name(self):
		return self.denon.nowPlaying["ALBUM"]
