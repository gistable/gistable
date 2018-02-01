"""
a simple stop loss bot.
adjust STOP_PRICE and STOP_VOLUME to your needs.
The file can be reloaded after editing without
restarting goxtool by simply pressing the l key.
"""
import strategy
import goxapi

# pylint: disable=C0301

# USD (EUR or other Fiat) price for the sell stop
# positive values are an absolute fixed price,
# negative values enable trailing stop mode and the
# value is the trailing distance
STOP_PRICE  = -5

# how many BTC to sell at or below the stop price
STOP_VOLUME = 0.01

class Strategy(strategy.Strategy):
    """a simple stoploss bot"""
    def __init__(self, gox):
        strategy.Strategy.__init__(self, gox)
        gox.history.signal_changed.connect(self.slot_changed)
        self.already_executed = False
        if STOP_PRICE < 0:
            self.debug("initializing trailing stop: %f @ %f" % (STOP_VOLUME, STOP_PRICE))
            self.stop_price = 0
            self.trail_distance = goxapi.float2int(-STOP_PRICE, gox.currency)
            gox.history.signal_changed(gox.history, None) # fire the signal once
        else:
            self.debug("initializing stop loss: %f @ %f" % (STOP_VOLUME, STOP_PRICE))
            self.stop_price = goxapi.float2int(STOP_PRICE, gox.currency)
            self.trail_distance = 0

    def slot_changed(self, history, _no_data):
        """price history has changed (new trades in history)"""
        if self.already_executed:
            return

        last_candle = history.last_candle()
        if not last_candle:
            return

        price_last =  last_candle.cls
        if self.trail_distance:
            price_trail = price_last - self.trail_distance
            if price_trail > self.stop_price:
                self.stop_price = price_trail
                self.debug("*** trailed stop to %f" %
                    goxapi.int2float(self.stop_price, self.gox.currency))

        if not self.stop_price:
            return

        if price_last <= self.stop_price:
            self.debug("*** market order: sell %f at %f" % (STOP_VOLUME, STOP_PRICE))
            self.gox.sell(0, int(STOP_VOLUME * 1e8))
            self.already_executed = True

    def slot_trade(self, gox, (date, price, volume, typ, own)):
        """a trade message has been received"""
        if not own:
            return

        vol = goxapi.int2float(volume, "BTC")
        prc = goxapi.int2float(price, gox.currency)
        self.debug("*** order filled: %f at %f %s" % (vol, prc, gox.currency))
