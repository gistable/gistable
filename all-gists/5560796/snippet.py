#!/usr/bin/env python
import smbus
import time


class Accel():
    def __init__(self, dev=1, g=2):
        self.bus = smbus.SMBus(dev)
        self.set_range(g)


    def write(self, register, data):
        self.bus.write_byte_data(0x1D, register, data)


    def read(self, data):
        return self.bus.read_byte_data(0x1D, data)


    def set_range(self, g):
        if g == 8:
            d = 0b01000001
        elif g == 4:
            d = 0b01001001
        elif g == 2:
            d = 0b01000101
        else:
            raise ValueError("Only 2, 4 or 8.")
        self.write(0x16, d)
        self.g = g


    def _get(self, addr):
        l = self.read(addr)
        h = self.read(addr + 1)
        d = h << 8 | l
        if d > 511:
            d -= 1024
        return d


    def get_x(self):
        return self._get(0x00)


    def get_y(self):
        return self._get(0x02)


    def get_z(self):
        return self._get(0x04)


    def clear_offset(self):
        self.write(0x10, 0)
        self.write(0x11, 0)
        self.write(0x12, 0)
        self.write(0x13, 0)
        self.write(0x14, 0)
        self.write(0x15, 0)
        time.sleep(0.1)


    def _set_offset(self, addr, zero):
        d = self._get(addr - 0x10)
        d = zero - d
        d = int(d * 2.5)
        d += 65536
        self.write(addr, d & 0xff) # Low
        self.write(addr + 1, d >> 8 & 0xff) # High


    def set_offset(self):
        self.clear_offset()
        self._set_offset(0x10, 0)
        self._set_offset(0x12, 0)
        if self.g == 4:
            zero = 32
        else:
            zero = 64
        self._set_offset(0x14, zero)
        time.sleep(0.1)


def main():
    mma = Accel(1)
    mma.set_offset()
    while True:
        x = mma.get_x()
        y = mma.get_y()
        z = mma.get_z()
        print("x =%4d ,y =%4d, z =%4d" % (x, y, z))
        time.sleep(0.1)


if __name__ == '__main__':
    main()