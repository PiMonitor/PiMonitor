'''
Created on 29-03-2013

@author: citan
'''
import serial
import time

from pimonitor.PMPacket import PMPacket

class PMConnection(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._ser = None
    
    def open(self):
        self._ser = serial.Serial(
                            port='/dev/ttyUSB0',
                            # port='/dev/tty.usbserial-000013FA',
                            baudrate=4800,
                            timeout=2000,
                            writeTimeout=55,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS)
        time.sleep(0.2)

    def close(self):
        if self._ser != None:
            self._ser.close()
        
    def init(self, target):
        request_packet = PMPacket(self.get_destination(target), 0xF0, [0xBF])
        return self.send_packet(request_packet)

    def send_packet(self, packet):
        self._ser.write(packet.to_string())
        time.sleep(0.05)
        
        out_packet = None
        tmp = []
        data = []

        while self._ser.inWaiting() > 0:
            tmp = []

            # read header
            tmp = self._ser.read(3)
            data.extend(tmp)

            # read size
            sizebytes = self._ser.read()
            data.append(sizebytes[0])
            size = ord(sizebytes[0])
            
            # read data
            tmp = self._ser.read(size)
            data.extend(tmp)

            # read checksum
            data.extend(self._ser.read())
            data = map(ord, data)

            out_packet = PMPacket.from_array(data)
            data = []

            if(packet.is_equal(out_packet)):
                continue

        return out_packet

    def read_parameter(self, parameter):
        address = parameter.get_address()
        address_len = parameter.get_address_length()

        data = []

        data.append(0xA8)
        data.append(0x00)
        for i in range(0, address_len):
            target_address = address + i
            data.append((target_address & 0xffffff) >> 16)
            data.append((target_address & 0xffff) >> 8)
            data.append(target_address & 0xff)
    
        request_packet = PMPacket(self.get_destination(parameter.get_target()), 0xf0, data)
        return self.send_packet(request_packet)

    def read_parameters(self, parameters):
        data = []
        target = parameters[0].get_target()
        
        data.append(0xA8)
        data.append(0x00)
        for parameter in parameters:
            # TODO:
            if target != parameter.get_target() and target & 0x01 != parameter.get_target() & 0x01 and target & 0x02 != parameter.get_target() & 0x02:
                raise Exception('connection', "targets differ: " + str(target) + " vs " + str(parameter.get_target()))

            address = parameter.get_address()
            address_len = parameter.get_address_length()
            for i in range(0, address_len):
                target_address = address + i
                data.append((target_address & 0xffffff) >> 16)
                data.append((target_address & 0xffff) >> 8)
                data.append(target_address & 0xff)
                
        request_packet = PMPacket(self.get_destination(target), 0xf0, data)
        out_packet = self.send_packet(request_packet)
        
        out_data = out_packet.get_data()
        out_packets = []
        data_offset = 1  # skip E8
        
        for parameter in parameters:
            address_len = parameter.get_address_length()
            single_out_data = [0xE8]
            single_out_data.extend(out_data[data_offset:address_len + data_offset])
            single_out_packet = PMPacket(out_packet.get_destination(), out_packet.get_source(), single_out_data);
            out_packets.append(single_out_packet)
            data_offset += address_len

        return out_packets
     
    def get_destination(self, target):
        dst = target
        if target == 1:
            dst = 0x10
        if target == 2:
            dst = 0x18
        if target == 3:
            dst = 0x10
        return dst
