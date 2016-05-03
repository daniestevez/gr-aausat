#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# 
# Copyright 2016 Daniel Estevez <daniel@destevez.net>.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import struct

class CSP(object):
    def __init__(self, csp_packet):
        csp = struct.unpack("<I", csp_packet[0:4])[0]
        self.priority = (csp >> 30) & 0x3
        self.source = (csp >> 25) & 0x1f
        self.destination = (csp >> 20) & 0x1f
        self.dest_port = (csp >> 14) & 0x3f
        self.source_port = (csp >> 8) & 0x3f
        self.reserved = (csp >> 4) & 0xf
        self.hmac = (csp >> 3) & 1
        self.xtea = (csp >> 2) & 1
        self.rdp = (csp >> 1) & 1
        self.crc = csp & 1

    def __str__(self):
        return ("""CSP header:
        Priority:\t{0}
        Source:\t{1}
        Destination:\t{2}
        Destination port:\t{3}
        Source port:\t{4}
        Reserved field:\t{5}
        HMAC:\t{6}
        XTEA:\t{7}
        RDP:\t{8}
        CRC:\t{9}""".format(
            self.priority, self.source, self.destination, self.dest_port,
            self.source_port, self.reserved, self.hmac, self.xtea, self.rdp,
            self.crc))

