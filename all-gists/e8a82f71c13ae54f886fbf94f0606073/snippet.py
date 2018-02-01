#!/usr/bin/env python3
import struct
from sys import stdin
import os
from io import FileIO

hiddev = os.open("/dev/hidraw5", os.O_RDWR | os.O_NONBLOCK)
pf = FileIO(hiddev, "wb+", closefd=False)
#pf=open("ds_my.bin", "wb+")

rumble_weak = 0
rumble_strong = 0
r = 0
g = 0
b = 10
crc = b'\x00\x00\x00\x00'
volume_speaker = 80
volume_l = 80
volume_r = 80
unk2 = 0x49
unk3 = 0x85
flash_bright = 0
flash_dark = 0
header = b'\x24'


def frame_number(inc):
	res = struct.pack("<H", frame_number.n)
	frame_number.n += inc
	if frame_number.n > 0xffff:
		frame_number.n = 0
	return res
frame_number.n = 0

def joy_data():
	data = [0xff,0x4,0x00]
	global volume_unk1,volume_unk2, unk3
	data.extend([rumble_weak,rumble_strong,r,g,b,flash_bright,flash_dark])
	data.extend([0]*8)
	data.extend([volume_l,volume_r,unk2,volume_speaker,unk3])
	return data

def _11_report():
	data = joy_data()
	data.extend([0]*(48))
	return b'\x11\xC0\x20' + bytearray(data) + crc

def _14_report(audo_data):
	return b'\x14\x40\xA0'+ frame_number(2) + header + audo_data + bytearray(40)

def _15_report(audo_data):
	data = joy_data();
	data.extend([0]*(52))
	return b'\x15\xC0\xA0' + bytearray(data)+ frame_number(2) + header + audo_data + bytearray(29)

def _17_report(audo_data):
	return b'\x17\x40\xA0' + frame_number(4) + header + audo_data + bytearray(4) + crc

stdin = stdin.detach()
data = bytearray()
count = 1
while True:
	if count % 6:
#	if True:
		data = _14_report(stdin.read(224)) if count % 3 else _15_report(stdin.read(224))
	else:
		data = _17_report(stdin.read(448))
	count+=1

	pf.write(data)
	
