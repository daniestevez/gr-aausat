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
        if len(eps_data) != EPS_LENGTH*2:
            raise InputException(len(eps_data), EPS_LENGTH)
        
        self.boot_count = int(eps_data[0:4], 16) # uint16_t
        self.uptime = int(eps_data[4:12], 16) # uint32_t
        self.rt_clock = int(eps_data[12:20], 16) # uint32_t
        self.ping_status = int(eps_data[20:22], 16) # uint8_t (?)
        self.subsystem_selfstatus = int(eps_data[22:26], 16) # uint16_t
        self.battery_voltage = int(eps_data[26:28], 16) * 40 # uint8_t - 40 magic number from MCC client
        self.cell_diff = int(eps_data[28:30], 16) * 4 # int8_t
        self.battery_current = int(eps_data[30:32], 16) * 10# int8_t
        self.solar_power = int(eps_data[32:34], 16) * 20 # uint8_t
        self.temp = int(eps_data[34:36], 16) #int8_t
        self.pa_temp = int(eps_data[36:38], 16) #int8_t
        self.main_voltage = int(eps_data[38:40], 16) #int8_t

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
        self.boot_count = int(com_data[0:4], 16) & 0x1FFF # uint16_t
        self.packets_received = int(com_data[4:8], 16) # uint16_t
        self.packets_send = int(com_data[8:12], 16) # uint16_t
        self.latest_rssi = struct.unpack('>h', com_data[12:16].decode('hex'))[0] # int16_t
        self.latest_bit_correction = int(com_data[16:18], 16) # uint8_t
        self.latest_byte_correction = int(com_data[18:20], 16) # uint8_t
        
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
# The beacon class takes a hex string of bytes as input, and parses it to generate
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
        if len(raw_data) != BEACON_LENGTH*2:
            raise InputException(len(raw_data), BEACON_LENGTH)

        self.subsystems = {}
        
        valid = int(raw_data[0:2], 16)

        #<subsystem>_LENGTH is given in bytes, two chars from the hex string is needed per byte
        eps_raw = raw_data[2:2+EPS_LENGTH*2]
        com_raw = raw_data[2+EPS_LENGTH*2:2+EPS_LENGTH*2+COM_LENGTH*2]
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

