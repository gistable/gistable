
import time
import logging

try:
    import serial
except ImportError:
    print('Python serial library required, on Ubuntu/Debian: ' +
          'apt-get install python-serial python3-serial')
    raise


class NovaPMSensor:
    """
    Nova PM Sensor SDS011 commands utilities as context manager.

    Read commands should be no more than one per 1 seconds. Query commands should be no more than one per 3 seconds.

    This code should work::

    with nova_sds011.NovaPMSensor('/dev/ttyUSB0') as sensor:
        data = sensor.read_data()
        logging.info(data)
        logging.info('set_sleep() %s', sensor.set_sleep())
        time.sleep(10)
        logging.info('set_working() %s', sensor.set_working())
        time.sleep(5)
        data = sensor.query_data()
        logging.info(data)

    TODO: correct handling of errors or logging
    TODO: fix retries

    Maybe more like https://github.com/igrr/aqi-sensor-demo/blob/master/Sds011.cpp
    """

    COMMAND = ([ord(b) for b in '\xAA\xB4'] +
               (13 * [0]) +
               [ord(b) for b in '\xFF\xFF\x00\xAB']
               )

    COMMAND_DELAY_SECONDS = 3

    def __init__(self, device_path='/dev/ttyUSB0'):
        self.device_path = device_path
        self.dev = None
        self._last_command_time = 0
        assert len(self.COMMAND) == 19

    def __enter__(self):
        self.dev = serial.Serial(self.device_path, 9600)
        if not self.dev.isOpen():
            self.dev.open()
        return self

    def __exit__(self, *args):
        if self.dev is not None:
            logging.debug('NovaPMSensor closing dev=%s', self.device_path)
            self.dev.close()

    def _checksum(self, data):
        return sum(v for v in data) % 256

    def _delay(self):
        diff = time.time() - self._last_command_time
        if self.COMMAND_DELAY_SECONDS - diff > 0:
            time.sleep(self.COMMAND_DELAY_SECONDS - diff)
        self._last_command_time = time.time()

    def read_data(self):
        """
        Read sensor data. Sensor should be in reporting mode.
        """
        self._delay()

        msg = self.dev.read(10)
        logging.debug('NovaPMSensor read_data() resp=%s', ''.join(['{:02X}'.format(b) for b in msg]))
        assert msg[0] == ord(b'\xAA')
        assert msg[1] == ord(b'\xC0'), 'Received {:02X}'.format(msg[1])
        assert msg[9] == ord(b'\xAB')
        assert msg[8] == self._checksum(msg[2:8])

        pm2_5 = (msg[3] * 256 + msg[2]) / 10.0
        pm10 = (msg[5] * 256 + msg[4]) / 10.0
        dev_id = ''.join(['{:02X}'.format(b) for b in msg[6:8]])
        return {'PM10': pm10, 'PM2_5': pm2_5, 'DEV_ID': dev_id}

    def query_data(self):
        """
        Set sensor in reporting mode and read data.
        """
        self._delay()

        cmd = self.COMMAND.copy()
        cmd[2] = 4
        cmd[17] = self._checksum(cmd[2:17])
        self.dev.write(bytearray(cmd))

        # for some reason first read may read previous command data
        try:
            return self.read_data()
        except AssertionError:
            pass
        return self.read_data()

    def _set_sleep(self, work):
        """
        Set sleep and work.

        :arg work: 1 to set to work, 0 to set to sleep
        :return: something for sleep
        """
        assert work in (0, 1)
        self._delay()
        cmd = self.COMMAND.copy()
        cmd[2] = 6
        cmd[3] = 1  # set mode
        cmd[4] = work
        cmd[17] = self._checksum(cmd[2:17])
        self.dev.write(bytearray(cmd))

        # for some reason first read may read previous command data
        resp = None
        for i in range(2):
            self._delay()
            if self.dev.in_waiting >= 10:
                resp = self.dev.read(10)
            else:
                continue
            resp_str = ''.join(['{:02X}'.format(b) for b in resp])
            logging.debug('NovaPMSensor _set_sleep(work=%s) resp=%s', work, resp_str)
            assert resp[0] == ord(b'\xAA')
            assert resp[9] == ord(b'\xAB')
            assert resp[8] == self._checksum(resp[2:8])

            if resp[1] == ord(b'\xC5'):
                break
            elif resp[1] == ord(b'\xC0'):
                # got data message
                continue
            else:
                raise Exception('Got strange response {}'.format(resp_str))

        # except serial.SerialException as err:
        #     if work_mode == 0:
        #         # maybe
        #         logging.debug('NovaPMSensor _set_sleep(work=%s) while read: %s assuming it is OK',
        #                       work_mode, repr(err))
        #         return None
        #     else:
        #         raise

        if not resp:
            raise Exception('NovaPMSensor _set_sleep(work=%s) nothing read', work)

        try:
            assert resp[1] == ord(b'\xC5'), 'Received {:02X}'.format(resp[1])
        except AssertionError as err:
            logging.debug('NovaPMSensor _set_sleep(work=%s) invalid resp[1]: %s nothing can be done',
                          work, repr(err))
            return None

        assert resp[2] == 6, 'Received {:02X}'.format(resp[2])
        assert resp[3] == work, 'Received {:02X}'.format(resp[3])
        return resp[4]

    def set_sleep(self):
        return self._set_sleep(work=0)

    def set_working(self):
        return self._set_sleep(work=1)