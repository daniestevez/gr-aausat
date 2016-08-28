#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The MIT License (MIT)
# 
# Copyright (c) 2016 Daniel Estévez
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

import numpy
from gnuradio import gr
import pmt
import array

import fec

class aausat4_fec(gr.basic_block):
    """
    docstring for block aausat4_fec
    """
    def __init__(self, verbose):
        gr.basic_block.__init__(self,
            name="aausat4_fec",
            in_sig=[],
            out_sig=[])

        self.verbose = verbose
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('out'))

        self.ec = fec.PacketHandler()

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return
        packet = str(bytearray(pmt.u8vector_elements(msg)))

        data = None
        try:
            if self.verbose:
                print "Trying to decode as long packet: 250 FEC bytes, 92 data bytes"
            (data, bit_corr, byte_corr) = self.ec.decode(packet[1:])
        except Exception as ex:
            if self.verbose: print(ex)
            try:
                if self.verbose:
                    print "Trying to decode as short packet: 128 FEC bytes, 31 data bytes"
                (data, bit_corr, byte_corr) = self.ec.decode(packet[1:1 + 128])
            except Exception as ex:
                if self.verbose: print(ex)

        if data:
            if self.verbose:
                print "FEC decoded OK. Bit errors: {}. Byte errors {}".format(bit_corr,
                                                                              byte_corr)
            data = data[:-2] # strip out HMAC
            self.message_port_pub(pmt.intern('out'),
                                  pmt.cons(pmt.PMT_NIL,
                                           pmt.init_u8vector(len(data), bytearray(data))))

