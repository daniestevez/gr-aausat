# Copyright (c) 2016 Jeppe Ledet-Pedersen <jlp@satlab.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import struct
import hashlib
import hmac
import ctypes
import codecs

VITERBI_RATE = 2
VITERBI_TAIL = 1
VITERBI_CONSTRAINT = 7

BITS_PER_BYTE = 8
MAX_FEC_LENGTH = 255

RS_LENGTH = 32
RS_BLOCK_LENGTH = 255

HMAC_LENGTH = 2
HMAC_KEY_LENGTH = 16
SIZE_LENGTH = 2

CSP_OVERHEAD = 4

SHORT_FRAME_LIMIT = 25
LONG_FRAME_LIMIT = 86

bbfec = ctypes.CDLL("libbbfec.so")

# viterbi
bbfec.create_viterbi.argtypes = [ctypes.c_int16]
bbfec.create_viterbi.restype = ctypes.c_void_p

bbfec.init_viterbi.argtypes = [ctypes.c_void_p, ctypes.c_int]
bbfec.init_viterbi.restype = ctypes.c_int

bbfec.update_viterbi.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint16]
bbfec.update_viterbi.restype = ctypes.c_int

bbfec.chainback_viterbi.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint]
bbfec.chainback_viterbi.restype = ctypes.c_int

bbfec.delete_viterbi.argtypes = [ctypes.c_void_p]
bbfec.delete_viterbi.restype = None

bbfec.encode_viterbi.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
bbfec.encode_viterbi.restype = None

# rs
bbfec.encode_rs.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
bbfec.encode_rs.restype = None

bbfec.decode_rs.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
bbfec.decode_rs.restype = ctypes.c_int

# randomizer
bbfec.ccsds_generate_sequence.argtypes = [ctypes.c_char_p, ctypes.c_int]
bbfec.ccsds_generate_sequence.restype = None

bbfec.ccsds_xor_sequence.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
bbfec.ccsds_xor_sequence.restype = None

TESTDATA = codecs.decode("8c1a48c0043fab4d3e790e2274af0a479c013770a2f889df13fefd825417b794470f240399b8562a8316f576861d7e72cf74bb29fcc0b6d6a5ce3659e8ee4d412bf95b7040459400ff3528f7f792c5f70c95eaf2574767eab615e26df977fc5ee837eda2eca7c601f4d568c9eca9d6f8ef015f67b98a79b2d8092fd60d2cee25", "hex")


class PacketHandler():
    def __init__(self, key=None, viterbi=True, rs=True, randomize=True):
        self.ccsds_sequence = ctypes.create_string_buffer(MAX_FEC_LENGTH)

        bbfec.ccsds_generate_sequence(self.ccsds_sequence, MAX_FEC_LENGTH)

        self.vp = bbfec.create_viterbi(MAX_FEC_LENGTH * BITS_PER_BYTE)

        self.key = hashlib.sha1(codecs.encode(key, "ascii")).digest()[:HMAC_KEY_LENGTH] if key else None
        self.viterbi = viterbi
        self.rs = rs
        self.randomize = randomize

    def __del__(self):
        bbfec.delete_viterbi(self.vp)

    def hexdump(self, src, length=16):
        filt = "".join([(len(repr(chr(x))) == 3) and chr(x) or "." for x in range(256)])
        offset = 0
        result = ""
        while src:
            s, src = src[:length], src[length:]
            hexa = ' '.join(["{0:02X}".format(x) for x in s])
            s = s.translate(filt)
            result += "{0:08X}   {1:{width}}   {2}\n".format(offset, hexa, s, width=length * 3)
            offset += length
        return result[:-1]

    def tx_frame_length(self, data):
        return SIZE_LENGTH + CSP_OVERHEAD + (SHORT_FRAME_LIMIT if (data - CSP_OVERHEAD) <= SHORT_FRAME_LIMIT else LONG_FRAME_LIMIT)

    def hmac_append(self, data):
        size = len(data) - CSP_OVERHEAD + HMAC_LENGTH
        hmkey = hmac.new(self.key, data[:CSP_OVERHEAD + size], hashlib.sha1).digest()[:HMAC_LENGTH]

        return data + hmkey

    def hmac_verify(self, data):
        size = len(data) - CSP_OVERHEAD - HMAC_LENGTH

        hmkey = hmac.new(self.key, data[:CSP_OVERHEAD + size], hashlib.sha1).digest()[:HMAC_LENGTH]
        hmpkg = data[CSP_OVERHEAD + size:CSP_OVERHEAD + size + HMAC_LENGTH]

        if hmkey != hmpkg:
            raise Exception("HMAC does not match expected value!")

        return data[:CSP_OVERHEAD + size]

    def decode(self, data):
        rx_length = int(len(data))
        data_mutable = ctypes.create_string_buffer(data)
        bit_corr = 0
        byte_corr = 0

        if self.viterbi:
            rx_length = (rx_length / VITERBI_RATE) - VITERBI_TAIL
            bbfec.init_viterbi(self.vp, 0)
            bbfec.update_viterbi(self.vp, data_mutable, int((rx_length * BITS_PER_BYTE) + (VITERBI_CONSTRAINT - 1)))
            bit_corr = bbfec.chainback_viterbi(self.vp, data_mutable, int(rx_length * BITS_PER_BYTE), int(0))

        if self.randomize:
            bbfec.ccsds_xor_sequence(data_mutable, self.ccsds_sequence, int(rx_length))

        if self.rs:
            pad = RS_BLOCK_LENGTH - RS_LENGTH - (rx_length - RS_LENGTH)
            byte_corr = bbfec.decode_rs(data_mutable, None, 0, int(pad))
            rx_length = rx_length - RS_LENGTH
            if byte_corr == -1:
                raise Exception("Reed-Solomon decoding error")

        size = struct.unpack(">H", data_mutable[:SIZE_LENGTH])[0]

        return data_mutable[SIZE_LENGTH:SIZE_LENGTH + CSP_OVERHEAD + size], bit_corr, byte_corr

    def encode(self, data):
        tx_length = self.tx_frame_length(len(data))
        data = struct.pack(">H", len(data) - CSP_OVERHEAD) + data
        data_mutable = ctypes.create_string_buffer(data, MAX_FEC_LENGTH)

        if self.rs:
            pad = RS_BLOCK_LENGTH - RS_LENGTH - tx_length
            bbfec.encode_rs(data_mutable, ctypes.cast(ctypes.byref(data_mutable, tx_length), ctypes.POINTER(ctypes.c_char)), pad)
            tx_length += RS_LENGTH

        if self.randomize:
            bbfec.ccsds_xor_sequence(data_mutable, self.ccsds_sequence, tx_length)

        if self.viterbi:
            bbfec.encode_viterbi(data_mutable, data_mutable, tx_length * BITS_PER_BYTE)
            tx_length = (tx_length + VITERBI_TAIL) * VITERBI_RATE

        return data_mutable[0:tx_length]

    def deframe(self, data):
        data, bit_corr, byte_corr = self.decode(data)
        data = self.hmac_verify(data) if self.key else data
        return data, bit_corr, byte_corr

    def frame(self, data):
        data = self.hmac_append(data) if self.key else data
        data = self.encode(data)
        return data

if __name__ == "__main__":
    key = sys.argv[1]
    ec = PacketHandler(key)
    print("Original data:\n{0}\n".format(ec.hexdump(TESTDATA)))
    data, bit_corr, byte_corr = ec.deframe(TESTDATA)
    print("Decoded data: ({0},{1})\n{2}\n".format(bit_corr, byte_corr, ec.hexdump(data)))
    data = ec.frame(data)
    print("Encoded data:\n{0}".format(ec.hexdump(data)))
