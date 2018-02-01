# Copyright 2008-2009 WebDriver committers
# Copyright 2008-2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from selenium.common.exceptions import StaleElementReferenceException

def stale(fn):
    def wrapper(self, *args):
        if self.changed:
            raise StaleElementReferenceException()
        return fn(self, *args)
    return wrapper

class HTML5Media(object):
    # error state
    @property
    def error(self):
        if self.changed:
            raise StaleElementReferenceException()
        errors = {
            1: "MEDIA_ERR_ABORTED",
            2: "MEDIA_ERR_NETWORK",
            3: "MEDIA_ERR_DECODE",
            4: "MEDIA_ERR_SRC_NOT_SUPPORTED"
        }
        return errors[self._el._parent.execute_script("return arguments[0].error", self._el)]
    
    # network state
    @property
    @stale
    def src(self):
        return self._el._parent.execute_script("return arguments[0].src", self._el)

    @src.setter
    def src(self, value):
        if isinstance(value, str):
            self._el._parent.execute_script("arguments[0].src = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a string")

    @property
    @stale
    def current_source(self):
        """Returns the current source of the video"""
        return self._el._parent.execute_script("return arguments[0].currentSrc", self._el)

    @property
    @stale
    def cross_origin(self):
        return self._el._parent.execute_script("return arguments[0].crossOrigin", self._el)

    @cross_origin.setter
    def cross_origin(self, value):
        if isinstance(value, str):
            self._el._parent.execute_script("arguments[0].crossOrigin = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a string")

    @property
    @stale
    def network_state(self):
        """Returns the string representation of the current network state"""
        states = {
            0: "NETWORK_EMPTY",
            1: "NETWORK_IDLE",
            2: "NETWORK_LOADING",
            3: "NETWORK_NO_SOURCE",
        }
        return states[self._el._parent.execute_script("return arguments[0].networkState", self._el)]

    @property
    @stale
    def preload(self):
        return self._el._parent.execute_script("return arguments[0].preload", self._el)

    @preload.setter
    def preload(self, value):
        if value in ["none", "metadata", "auto"]:
            self._el._parent.execute_script("arguments[0].preload = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be either 'none', 'metadata' or 'auto'")

    @property
    @stale
    def buffered(self):
        """Returns the current source of the video"""
        return self._el._parent.execute_script("return arguments[0].buffered", self._el)

    @stale
    def load(self):
        self._el._parent.execute_script("arguments[0].load()", self._el)

    @stale
    def can_play_type(self, media_type):
        return self._el._parent.execute_script("return arguments[0].canPlayType(arguments[1])", self._el, media_type)

    # ready state
    @property
    @stale
    def ready_state(self):
        states = {
            0: "HAVE_NOTHING",
            1: "HAVE_METADATA",
            2: "HAVE_CURRENT_DATA",
            3: "HAVE_FUTURE_DATA",
            4: "HAVE_ENOUGH_DATA"
        }
        return states[self._el._parent.execute_script("return arguments[0].readyState", self._el)]

    @property
    @stale
    def seeking(self):
        return self._el._parent.execute_script("return arguments[0].seeking", self._el)
    
    # playback state
    @property
    @stale
    def current_time(self):
        return self._el._parent.execute_script("return arguments[0].currentTime", self._el)

    @current_time.setter
    def current_time(self, value):
        if isinstance(value, int):
            self._el._parent.execute_script("arguments[0].currentTime = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a boolean")

    @property
    @stale
    def initial_time(self):
        return self._el._parent.execute_script("return arguments[0].initialTime", self._el)
    
    @property
    @stale
    def duration(self):
        return self._el._parent.execute_script("return arguments[0].duration", self._el)

    @property
    @stale
    def start_offset_time(self):
        return self._el._parent.execute_script("return arguments[0].startOffsetTime", self._el)

    @property
    @stale
    def paused(self):
        return self._el._parent.execute_script("return arguments[0].paused", self._el)

    @property
    @stale
    def default_playback_rate(self):
        return self._el._parent.execute_script("return arguments[0].defaultPlaybackRate", self._el)

    @default_playback_rate.setter
    def default_playback_rate(self, value):
        if isinstance(value, int):
            self._el._parent.execute_script("arguments[0].defaultPlaybackRate = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a int")

    @property
    @stale
    def playback_rate(self):
        return self._el._parent.execute_script("return arguments[0].playbackRate", self._el)

    @playback_rate.setter
    def playback_rate(self, value):
        if isinstance(value, int):
            self._el._parent.execute_script("arguments[0].playbackRate = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a int")

    @property
    @stale
    def played(self):
        return self._el._parent.execute_script("return arguments[0].played", self._el)

    @property
    @stale
    def seekable(self):
        return self._el._parent.execute_script("return arguments[0].seekable", self._el)

    @property
    @stale
    def ended(self):
        return self._el._parent.execute_script("return arguments[0].ended", self._el)

    @property
    @stale
    def autoplay(self):
        return self._el._parent.execute_script("return arguments[0].autoplay", self._el)

    @autoplay.setter
    def autoplay(self, value):
        if isinstance(value, bool):
            self._el._parent.execute_script("arguments[0].autoplay = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a boolean")

    @property
    @stale
    def loop(self):
        return self._el._parent.execute_script("return arguments[0].loop", self._el)

    @loop.setter
    def loop(self, value):
        if isinstance(value, bool):
            self._el._parent.execute_script("arguments[0].loop = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a boolean")

    @stale
    def play(self):
        x = self._el._parent.execute_script("arguments[0].play()", self._el)

    @stale
    def pause(self):
        x = self._el._parent.execute_script("arguments[0].pause()", self._el)

    # media controller
    @property
    @stale
    def mediagroup(self):
        return self._el._parent.execute_script("return arguments[0].mediagroup", self._el)

    @mediagroup.setter
    def mediagroup(self, value):
        if isinstance(value, str):
            self._el._parent.execute_script("arguments[0].mediagroup = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a string")

    # controls
    @property
    @stale
    def controls(self):
        return self._el._parent.execute_script("return arguments[0].controls", self._el)

    @controls.setter
    def controls(self, value):
        if isinstance(value, bool):
            self._el._parent.execute_script("arguments[0].controls = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a boolean")

    @property
    @stale
    def volume(self):
        return self._el._parent.execute_script("return arguments[0].volume", self._el)

    @volume.setter
    def volume(self, value):
        if isinstance(value, int):
            self._el._parent.execute_script("arguments[0].volume = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a int")

    @property
    @stale
    def muted(self):
        return self._el._parent.execute_script("return arguments[0].muted", self._el)

    @muted.setter
    def muted(self, value):
        if isinstance(value, bool):
            self._el._parent.execute_script("arguments[0].muted = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a boolean")

    @property
    @stale
    def default_muted(self):
        return self._el._parent.execute_script("return arguments[0].defaultMuted", self._el)

    @default_muted.setter
    def default_muted(self, value):
        if isinstance(value, bool):
            self._el._parent.execute_script("arguments[0].defaultMuted = arguments[1]", self._el, value)
            self.changed = True
        else:
            raise ValueError("value needs to be a boolean")

class Video(HTML5Media):
    def __init__(self, webelement):
        """
        Constructor. A check is made that the given element is, indeed, a VIDEO tag. If it is not,
        then an UnexpectedTagNameException is thrown.

        :Args:
         - webelement - element VIDEO element to wrap
        
        Example:
            from selenium.webdriver.support.ui import Select \n
            Video(driver.find_element_by_tag_name("video")).play()
        """
        if webelement.tag_name.lower() != "video":
            raise UnexpectedTagNameException(
                "Video only works on <video> elements, not on <%s>" % 
                webelement.tag_name)
        self._el = webelement
        self.changed = False

    @property
    @stale
    def width(self):
        """Returns the width in px of the video"""
        return self._el._parent.execute_script("return arguments[0].width", self._el)

    @width.setter
    def width(self, value):
        """Sets the width in px of the video"""
        self._el._parent.execute_script("arguments[0].width = arguments[1]", self._el, value)
        self.changed = True

    @property
    @stale    
    def video_width(self):
        """Returns the width in px of the video"""
        return self._el._parent.execute_script("return arguments[0].videoWidth", self._el)

    @property
    @stale
    def height(self):
        """Returns the height in px of the video"""
        return self._el._parent.execute_script("return arguments[0].height", self._el)

    @height.setter
    def height(self, value):
        """Sets the width in px of the video"""
        self._el._parent.execute_script("arguments[0].height = arguments[1]", self._el, value)
        self.changed = True

    @property
    @stale
    def video_height(self):
        """Returns the height in px of the video"""
        return self._el._parent.execute_script("return arguments[0].videoHeight", self._el)

    @property
    @stale
    def poster(self):
        return self._el._parent.execute_script("return arguments[0].poster", self._el)

    @poster.setter
    def poster(self, value):
        self._el._parent.execute_script("arguments[0].poster = arguments[1]", self._el, value)
        self.changed = True

class Audio(HTML5Media):
    def __init__(self, webelement):
        """
        Constructor. A check is made that the given element is, indeed, a Audio tag. If it is not,
        then an UnexpectedTagNameException is thrown.

        :Args:
         - webelement - element Audio element to wrap

        Example:
            from selenium.webdriver.support.ui import Select \n
            Audi(driver.find_element_by_tag_name("audio")).play()
        """
        if webelement.tag_name.lower() != "audio":
            raise UnexpectedTagNameException(
                "Audio only works on <audio> elements, not on <%s>" % 
                webelement.tag_name)
        self._el = webelement
        self.changed = False

if __name__ == "__main__":
    from selenium import webdriver
    
    driver = webdriver.Firefox()

    driver.get("http://html5demos.com/video")
    e = driver.find_element_by_css_selector("video")
    v = Video(e)
    v.play()

    import time
    time.sleep(5)

    v.pause()
    v.width = 600
    e = driver.find_element_by_css_selector("video")
    v = Video(e)
    print("Width: {0}".format(v.width))
    v.height = 500
    e = driver.find_element_by_css_selector("video")
    v = Video(e)
    print("Height: {0}".format(v.height))
    print("Current Source: {0}".format(v.current_source))
    print("Network State: {0}".format(v.network_state))
    print("Ready State: {0}".format(v.ready_state))
    print("Buffered: {0}".format(v.buffered))
    print("Can Play Type? (video/ogg): {0}".format(v.can_play_type("video/ogg")))
    print("Can Play Type? (video/mp4): {0}".format(v.can_play_type("video/mp4")))
    print("Can Play Type? (video/webm): {0}".format(v.can_play_type("video/webm")))
    print("Seeking: {0}".format(v.seeking))
    print("Duration: {0}".format(v.duration))
    print("Paused?: {0}".format(v.paused))
    print("Played: {0}".format(v.played))
    print("Seekable: {0}".format(v.seekable))
    print("Ended?: {0}".format(v.ended))

    driver.quit()