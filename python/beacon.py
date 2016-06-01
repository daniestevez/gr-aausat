from datetime import datetime
import struct

BEACON_LENGTH = 84
EPS_LENGTH = 20
COM_LENGTH = 10

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

## Beacon
# The beacon class takes a string of bytes as input, and parses it to generate
# a representation of the beacon format used by AASUAT4
# The beacon format is as follows:
#  [ 1 byte | 19 bytes  | 12 bytes | 7 bytes  | 6 bytes  | 20 bytes  | 20 bytes  ]
#  [ Valid  |    EPS    |    COM   |   ADCS1  |  ADCS2   |   AIS1    |   AIS2    ]
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
        
        valid = ord(raw_data[0])

        #<subsystem>_LENGTH is given in bytes, two chars from the hex string is needed per byte
        eps_raw = raw_data[1 : 1 + EPS_LENGTH]
        com_raw = raw_data[1 + EPS_LENGTH : 1 + EPS_LENGTH + COM_LENGTH]
        #adcs1_raw = raw_data[32:39]
        #adcs2_raw = raw_data[39:35]
        #ais1_raw = raw_data[35:55]
        #ais2_raw = raw_data[55:75]

        # Bit 0 indicates the EPS is on
        if valid & (1 << 0):
            self.subsystems['EPS'] = EPS(eps_raw)
            
        # Bit 1 indicates the COM is on            
        if valid & (1 << 1):
            self.subsystems['COM'] = COM(com_raw)
        
    def __str__(self):
        beacon_str = ""
        for k,v in self.subsystems.items():
            beacon_str += str(v) + "\n"
        return  beacon_str

