#!/usr/bin/python
import sys
import time
import difflib
import pigpio
import struct
import binascii

RX=18

try:
    pi = pigpio.pi()
    pi.set_mode(RX, pigpio.INPUT)
    pi.bb_serial_read_open(RX, 9600, 8)
    while 1:
        (count, data) = pi.bb_serial_read(RX)
        if count == 32 and data[0] == 0x42 and data[1] == 0x4d:
            s = (struct.Struct(">"+"H"*16)).unpack(data)
            print(s)
        time.sleep(1)
except:
    pi.bb_serial_read_close(RX)
    pi.stop()
