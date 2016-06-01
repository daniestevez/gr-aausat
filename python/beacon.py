from datetime import datetime
import struct

BEACON_LENGTH = 84
EPS_LENGTH = 20
COM_LENGTH = 10

# reverse engineered
ADCS1_LENGTH = 7
ADCS2_LENGTH = 6
AIS_LENGTH = 20

class InputException(Exception):
    def __init__(self, got, expected):
        msg = "Unexpected length: got {0}, expected {1}".format(got, expected) 
        super(Exception, self).__init__(msg)
        
class EPS(object):
    def __init__(self, eps_data):
        if len(eps_data) != EPS_LENGTH:
            raise InputException(len(eps_data), EPS_LENGTH)

        self.boot_count, self.uptime, self.rt_clock, self.ping_status, self.subsystem_status,\
        self.battery_voltage, self.cell_diff, self.battery_current, self.solar_power,\
        self.temp, self.pa_temp, self.main_voltage = struct.unpack(">HIIBHBbbBbbb", eps_data)

        self.battery_voltage *= 40
        self.cell_diff *= 4
        self.battery_current *= 10
        self.solar_power *= 20

    def __str__(self):
        eps_str = ("""EPS:
        Boot count:\t\t{0}
        Up time:\t\t{1} seconds
        Real time clock:\t{2}
        Battery voltage:\t{3} mV
        Cell difference:\t{4:.1f} mV
        Battery current:\t{5} mA
        Solar power:\t\t{6}
        Temperature:\t\t{7} C
        PA temperature:\t\t{8} C""".format(
            self.boot_count, self.uptime, datetime.fromtimestamp(self.rt_clock),
            self.battery_voltage, self.cell_diff, self.battery_current, self.solar_power,
            self.temp, self.pa_temp))

        return eps_str


class COM(object):
    def __init__(self, com_data):
        self.boot_count, self.packets_received, self.packets_send, self.latest_rssi,\
        self.latest_bit_correction, self.latest_byte_correction = \
                          struct.unpack(">HHHhBB", com_data)

        self.boot_count &= 0x1fff
        
    def __str__(self):
        com_str = ("""COM:
        Boot count:\t\t{0}
        Packets received:\t{1}
        Packets send:\t\t{2}
        Latest rssi:\t\t{3}
        Latest bit corrections:\t{4}
        Latest byte corrections:{5}""".format(
            self.boot_count, self.packets_received, self.packets_send,
            self.latest_rssi, self.latest_bit_correction, self.latest_byte_correction))

        return com_str

# Reverse engineered classes
class ADCS1(object):
    def __init__(self, adcs1_data):
        data = struct.unpack(">hhhB", adcs1_data)
        self.bdot = tuple(data[0:3])
        self.state = data[3]

    def __str__(self):
        adcs1_str = ("""ADCS1:
        State:\t{}
        Bdot:\t{}""".format(self.state, self.bdot))

        return adcs1_str

class ADCS2(object):
    def __init__(self, adcs2_data):
        self.gyro = tuple(struct.unpack(">hhh", adcs2_data))

    def __str__(self):
        adcs2_str = ("""ADCS2:
        Gyro:\t{}""".format(self.gyro))

        return adcs2_str

class AIS(object):
    def __init__(self, ais_data):
        # there are some fields which apparently are 0 all the time
        # this fields can't be identified by reverse engineering
        self.boot_count, _, _, self.unique_mssi, _ = struct.unpack(">HhhH12s", ais_data)

    def __str__(self):
        ais_str = ("""AIS:
        Boot count:\t{}
        Unique MSSI:\t{}""".format(self.boot_count, self.unique_mssi))

        return ais_str

## Beacon
# The beacon class takes a string of bytes as input, and parses it to generate
# a representation of the beacon format used by AASUAT4
# The beacon format is as follows:


#  [ 1 byte | 19 bytes  | 12 bytes | 7 bytes  | 6 bytes  | 20 bytes  | 20 bytes  ]
#  [ Valid  |    EPS    |    COM   |   ADCS1  |  ADCS2   |   AIS1    |   AIS2    ]
# This is not correct EPS is 20 bytes and COM is 10 bytes
# The remaining fields seem to have the correct length

#
# For each subsystem, which are valid, are the corresponding data bytes passed to another
# class which parses the information.
#
# The __str__ method returns a human readable string with key information from the beacon
class Beacon(object):
    
    def __init__(self, raw_data):
        if len(raw_data) != BEACON_LENGTH:
            raise InputException(len(raw_data), BEACON_LENGTH)

        self.subsystems = {}

        valid, eps_raw, com_raw, adcs1_raw, adcs2_raw, ais1_raw, ais2_raw = \
          struct.unpack(("B"+"{}s"*6).format(EPS_LENGTH, COM_LENGTH, ADCS1_LENGTH, ADCS2_LENGTH, AIS_LENGTH, AIS_LENGTH), raw_data)

        # reverse engineered valid bits
        # EPS and COM are known from university team code
        # valid byte is usually 0x27
        # in DK3WN's blog we see that EPS, COM, AIS2 and ADCS1 are valid
        eps_valid = valid & (1 << 0)
        com_valid = valid & (1 << 1)
        adcs1_valid = valid & (1 << 2)
        adcs2_valid = valid & (1 << 3)
        ais1_valid = valid & (1 << 4)
        ais2_valid = valid & (1 << 5)
        
        if eps_valid:
            self.subsystems['EPS'] = EPS(eps_raw)
        if com_valid:
            self.subsystems['COM'] = COM(com_raw)
        if adcs1_valid:
            self.subsystems['ADCS1'] = ADCS1(adcs1_raw)
        if adcs2_valid:
            self.subsystems['ADCS2'] = ADCS2(adcs2_raw)
        if ais1_valid:
            self.subsystems['AIS1'] = AIS(ais1_raw)
        if ais2_valid:
            self.subsystems['AIS2'] = AIS(ais2_raw)
        
    def __str__(self):
        beacon_str = ""
        for k,v in self.subsystems.items():
            beacon_str += str(v) + "\n"
        return  beacon_str

