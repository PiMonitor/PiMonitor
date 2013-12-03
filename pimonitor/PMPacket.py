'''
Created on 13-04-2013

@author: citan
'''

import array
import binascii
import collections

class PMPacket(object):
	'''
	classdocs
	'''
# 0x80
# destination byte
# source byte
# data size byte
# ...
# checksum byte sum of every byte in packet (incl. header)

	_header_byte = 0x80
	_valid_bytes = [0xFF, 0xA8, 0xE8]
	
	def __init__(self, dst, src, data):
		self._dst = dst
		self._src = src
		self._data = data

	@classmethod
	def from_array(cls, data):
		validate = PMPacket.is_valid(data)
		if (not validate[0]):
			raise Exception('packet', validate[1])

		dst = data[1]
		src = data[2]
		data = data[4:-1]
		return cls(dst, src, data)

	@classmethod
	def is_valid(cls, data):
		# TODO: check E8
		valid = True
		msg = ""

		valid = valid and (len(data) > 5)
		msg += "invalid length (too short), " if (not valid) else ""

		valid = valid and (data[0] == PMPacket._header_byte)
		msg += "invalid header, " if (not valid) else ""

		
		#valid = data[4] in PMPacket._valid_bytes
		#msg += "invalid header, expected one of " + ', '.join(hex(s) for s in PMPacket._valid_bytes) +", got: " + hex(data[4]) + ", " if (not valid) else ""  
		#valid = valid and ((data[1] == 0x10) or (data[1] == 0xf0))
		#valid = valid and ((data[2] == 0x10) or (data[2] == 0xf0))
		#valid = valid and (data[1] != data[2])
		#msg += "invalid source/target, " if (not valid) else ""

		current_len = len(data)
		expected_len = 5 + data[3]
		valid = valid and (current_len == expected_len)
		msg += "invalid length (is: " + str(current_len) + ", expected: " + str(expected_len) + "), " if (not valid) else ""

		checksum = 0
		for i in range(0, len(data) - 1):
			checksum = (checksum + data[i]) & 0xFF

		valid = valid and (checksum == data[-1])
		msg += "invalid checksum (is " + str(checksum) + ", expected: " + str(data[-1]) + "), " if (not valid) else ""

		return valid, msg

	def is_equal(self, packet):
		return self.to_bytes() == packet.to_bytes()

	def to_bytes(self):
		length = len(self._data)

		packet = [self._header_byte, self._dst, self._src, length]
		packet.extend(self._data)

		checksum = 0
		for b in packet:
			checksum = (checksum + b) & 0xFF

		packet.append(checksum)
		return packet

	def to_string(self):
		return array.array('B', self.to_bytes()).tostring()

	def dump(self):
		return "["+ ', '.join(("0x%0.2X" % s) for s in self.to_bytes()) + "], dst: " + hex(self._dst) + ", src: " + hex(self._src) + ", len: " + str(len(self._data))

	def get_data(self):
		return self._data

	def get_destination(self):
		return self._dst

	def get_source(self):
		return self._src
	
	def get_romid(self):
		if self._data[0] != 0xFF:
			raise Exception('packet', "not valid init response")
		if len(self._data) < 9:
			raise Exception('packet', "not valid init response")
		rom_id = ((self._data[4] << 32) | (self._data[5] << 24) | (self._data[6] << 16) | (self._data[7] << 8) | (self._data[8])) & 0xFFFFFFFFFF
		return hex(rom_id).lstrip("0x").upper()

	@classmethod
	def dump_header(cls, data):
		print("header ["+ ', '.join(hex(s) for s in data) +"], len: " + str(len(data)))
