#
# https://docs.gdax.com/#websocket-feed
#
import websocket
import sys
from datetime import datetime, timedelta, timezone

import sched, time
import json

JST = timezone(timedelta(hours=+9), 'JST')

class GdaxStream():
    endpoint = "wss://ws-feed.gdax.com"
    def __init__(self):
        #websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
                GdaxStream.endpoint,
                on_message = self.on_message, 
                on_error = self.on_error, 
                on_close = self.on_close
         )
        self.ws.on_open = self.on_open

        try:
            self.run()
        except KeyboardInterrupt:
            self.ws.close()

    def run(self):
        print("### run ###")
        self.ws.run_forever()
        pass

    def on_message(self, ws, message):
        now = datetime.now(JST)
        print(str(now), message)
    
    def on_error(self, ws, error):
        print(error)
        sys.exit()
    
    def on_close(self, ws):
        print("### closed ###")
    
    def on_open(self, ws):
        print("### open ###")
        ws.send(json.dumps({"type": "subscribe","product_ids": ["BTC-USD"]}))

if __name__=="__main__":
    GdaxStream()