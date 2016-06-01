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

import numpy
from gnuradio import gr

from collections import deque
import binascii

import fec
import beacon
from csp.csp_header import CSP

MAXLEN = 2008

def pack(s):
    d = bytearray()
    for i in range(0, len(s), 8):
        x = 0
        for j in range(8):
            x <<= 1
            x += s[i+j]
        d.append(x)
    return bytes(d)

class aausat_parser(gr.sync_block):
    """
    docstring for block beacon_parser
    Expecting an unpacked byte stream as input (one byte per bit LSB)
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="aausat_parser",
            in_sig=[numpy.byte],
            out_sig=None)
        self.stream = deque(maxlen=MAXLEN - 1)
        self.ec = fec.PacketHandler()


    def process_packet(self, packet):
        print "FSM = ", binascii.b2a_hex(pack(packet[:8]))

        data = None
        try:
            print "Trying to decode as long packet: 250 FEC bytes, 92 data bytes"
            (data, bit_corr, byte_corr) = self.ec.decode(pack(packet[8:]))
        except Exception as ex:
            print(ex)
            try:
                print "Trying to decode as short packet: 128 FEC bytes, 31 data bytes"
                (data, bit_corr, byte_corr) = self.ec.decode(pack(packet[8:8 + 128*8]))
            except Exception as ex:
                print(ex)

        if data:
            hexdata = binascii.b2a_hex(data)
            print "--------- CSP PACKET -------------"
            print "data = ", hexdata
            print "length = ", len(data), " bytes"
            print "bit_corr = ", bit_corr
            print "byte_corr = ", byte_corr
            print "----------------------------------"
            print(str(CSP(data)))
            try:
                print(str(beacon.Beacon(data[4:-2]))) # -2 strips out HMAC
            except beacon.InputException:
                print "Error decoding beacon"

        return


    def work(self, input_items, output_items):
        inp = input_items[0]

        # tags for packets already in inp
        tags = self.get_tags_in_window(0, 0, max(len(inp) - MAXLEN + 1, 0))
        for tag in tags:
            #print "-----tag----"
            #print(tag.key)
            #print(tag.offset)
            #print "------------"
            start = tag.offset - self.nitems_read(0)
            self.process_packet(inp[start:start + MAXLEN].tolist())
        
        # tags for packets with beginning in self.stream and ending in inp
        ##print "self.nitems_read(0) = ", self.nitems_read(0)
        ##print "len(self.stream) = ", len(self.stream)
        ##print "len(inp) = ", len(inp)
        tags = self.get_tags_in_range(0, self.nitems_read(0) - len(self.stream), max(self.nitems_read(0) + min(len(inp) - MAXLEN + 1, 0),0))
        for tag in tags:
            #print "--tag--"
            #print(tag.key)
            #print(tag.offset)
            #print "-----"
            start = tag.offset - self.nitems_read(0) + len(self.stream)
            end = tag.offset - self.nitems_read(0) + MAXLEN
            l = list(self.stream)[start:] + inp[:end].tolist()
            self.process_packet(l)

        self.stream.extend(inp.tolist())

        return len(inp)
