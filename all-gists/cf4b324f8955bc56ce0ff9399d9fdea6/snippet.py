import ds18x20
import gc
from machine import Timer, Pin
import network
import onewire
from time import sleep_ms
from umqtt.simple import MQTTClient
import urandom


PIN_TEMP = 5


def send_temp(t):
    c = MQTTClient('clientname', '<mqtt_server_ip>')
    c.connect()
    c.publish('/topic/temp1', str(t))
    sleep_ms(500)
    print('Sent!')
    c.disconnect()


def read_temp():
    ds = ds18x20.DS18X20(onewire.OneWire(Pin(5)))
    roms = ds.scan()
    ds.convert_temp()
    sleep_ms(100)
    # assume there is only 1 probe
    return ds.read_temp(roms[0])

def run():
    # tim = Timer(-1)
    # tim.init(period=2000, mode=Timer.PERIODIC, callback=send_temp)
    wlan = network.WLAN(network.STA_IF)

    while True:
        try:
            if wlan.isconnected():
                t = read_temp()
                send_temp(t)
                sleep_ms(10000)
            else:
                sleep_ms(1000)
        except:
            pass


run()