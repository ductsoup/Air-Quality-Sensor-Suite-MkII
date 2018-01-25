#!/usr/bin/env python

import struct
from math import pi

j = struct.unpack('>HH',struct.pack('>f', pi))
print(pi)
print("%04x %04x" % j)
