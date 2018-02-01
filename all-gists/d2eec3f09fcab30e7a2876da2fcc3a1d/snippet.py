# pip3 install tornado pubnub python-dateutil
# python3 -u sfd.py | tee sfd.log
from multiprocessing import Process, Value, Lock, Event
from datetime import datetime
import dateutil.parser
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_tornado import PubNubTornado
from pubnub.pnconfiguration import PNReconnectionPolicy

class SFDInfo():
    def __init__(self):
        self._fx_ltp = Value('i', 0)
        self._btc_ltp = Value('i', 0)
        self._disparity = Value('d', 0)
        self._updated_at = Value('d', 0)
        self._last_sfd_at = Value('d', 0)
        self.lock = Lock()
        self.event = Event()

    @property
    def fx_ltp(self):
        return self._fx_ltp.value
    @fx_ltp.setter
    def fx_ltp(self, val):
        self._fx_ltp.value = int(val)

    @property
    def btc_ltp(self):
        return self._btc_ltp.value
    @btc_ltp.setter
    def btc_ltp(self, val):
        self._btc_ltp.value = int(val)

    @property
    def updated_at(self):
        return datetime.fromtimestamp(self._updated_at.value)
    @updated_at.setter
    def updated_at(self, d):
        self._updated_at.value = d.timestamp()

    @property
    def last_sfd_at(self):
        return datetime.fromtimestamp(self._last_sfd_at.value)
    @last_sfd_at.setter
    def last_sfd_at(self, d):
        self._last_sfd_at.value = d.timestamp()

    @property
    def disparity(self):
        return self._disparity.value
    @disparity.setter
    def disparity(self, val):
        self._disparity.value = val

    @property
    def ready(self):
        return self.fx_ltp > 0 and self.btc_ltp > 0

    # for me (-_-)
    def unsafe_with_lock(self, side, unsafe_range=0.25):
        with self.lock:
            return self.unsafe(side, unsafe_range)

    def unsafe(self, side, unsafe_range=0.25):
        assert(side == "BUY" or side == "SELL")
        disp = self.disparity
        if side == "BUY":
            return \
                (10.0 - unsafe_range < disp and disp < 10.0 + unsafe_range) or \
                (15.0 - unsafe_range < disp and disp < 15.0 + unsafe_range) or \
                (20.0 - unsafe_range < disp and disp < 20.0 + unsafe_range)
        else:
            return \
                (-10.0 - unsafe_range < disp and disp < -10.0 + unsafe_range) or \
                (-15.0 - unsafe_range < disp and disp < -15.0 + unsafe_range) or \
                (-20.0 - unsafe_range < disp and disp < -20.0 + unsafe_range)

def sfd_process(sfd):
    FX_CHANNEL = "lightning_ticker_FX_BTC_JPY"
    BTC_CHANNEL = "lightning_ticker_BTC_JPY"
    class BitflyerSubscriberCallback(SubscribeCallback):
        def message(self, pubnub, message):
            tick = message.message
            timestamp = dateutil.parser.parse(tick["timestamp"])
            with sfd.lock:
                changed = False
                if message.channel == FX_CHANNEL:
                    if sfd.fx_ltp != tick["ltp"]:
                        sfd.fx_ltp = tick["ltp"]
                        changed = True
                elif message.channel == BTC_CHANNEL:
                    if sfd.btc_ltp != tick["ltp"]:
                        sfd.btc_ltp = tick["ltp"]
                        changed = True
                if sfd.ready and changed:
                    sfd.disparity = (sfd.fx_ltp / sfd.btc_ltp) * 100 - 100
                    if (sfd.fx_ltp > sfd.btc_ltp and sfd.disparity >= 10.0) or \
                       (sfd.fx_ltp < sfd.btc_ltp and sfd.disparity <= -10.0):
                        sfd.last_sfd_at = timestamp
                    sfd.updated_at = timestamp
                    sfd.event.set()

    config = PNConfiguration()
    config.subscribe_key = 'sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f'
    config.reconnect_policy = PNReconnectionPolicy.LINEAR
    config.ssl = False
    config.set_presence_timeout(60)
    pubnub = PubNubTornado(config)
    listener = BitflyerSubscriberCallback()
    pubnub.add_listener(listener)
    pubnub.subscribe().channels([FX_CHANNEL, BTC_CHANNEL]).execute()
    pubnub.start()

if __name__ == '__main__':
    from time import sleep

    EVENT_DRIVEN = True
    FACE_D = "danger (ﾟДﾟ)"
    FACE_N = "normal (・∀・)"

    sfd = SFDInfo()
    proc1 = Process(target=sfd_process, args=(sfd,))
    proc1.start()

    while True:
        if EVENT_DRIVEN:
            sfd.event.wait()
            sfd.event.clear()
        else:
            sleep(1)
            if not sfd.ready:
                continue

        with sfd.lock:
            buy = FACE_D if sfd.unsafe("BUY") else FACE_N
            sell = FACE_D if sfd.unsafe("SELL") else FACE_N

            print("{}, fx: {}, btc: {}, disparity: {:.2f}%, last_sfd: {}, buy: {}, sell: {}".format(
                sfd.updated_at,
                sfd.fx_ltp, sfd.btc_ltp,
                sfd.disparity, 
                sfd.last_sfd_at,
                buy, sell
            ))
