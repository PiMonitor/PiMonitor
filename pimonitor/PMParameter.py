'''
Created on 29-03-2013

@author: citan
'''

import re

class PMParameter(object):
	'''
	classdocs
	'''

	def __init__(self, pid, name, desc, byte_index, bit_index, target):
		'''
		Constructor
		'''
		self._id = pid
		self._name = name
		self._desc = desc
		self._byte_index = byte_index
		self._bit_index = bit_index
		self._target = target
		self._conversions = []
		self._dependencies = []
		self._parameters = []
		self._address = 0
		self._address_length = 0

	def get_id(self):
		return self._id;

	def set_address(self, address, length):
		self._address = address
		self._address_length = length

	def get_address(self):
		return self._address

	def get_address_length(self):
		return self._address_length

	def get_target(self):
		return self._target

	def get_name(self):
		return self._name
	
	def add_conversion(self, conversion):
		self._conversions.append(conversion)
	
	def add_dependency(self, dependency):
		self._dependencies.append(dependency)

	def get_dependencies(self):
		return self._dependencies

	def add_parameter(self, parameter):
		self._parameters.append(parameter)

	def get_parameters(self):
		return self._parameters
		
	def get_calculated_value(self, packets, unit=None):
		value = ""
		local_vars = locals()
		
		if len(self._conversions) > 0 and unit == None:
			unit = self._conversions[0][0]
			
		for conversion in self._conversions:
			currunit = conversion[0]
			expr = conversion[1]
			value_format = conversion[2]
			conversion_map = {}		
			if unit == currunit:
				param_pairs = re.findall(r'\[([^]]*)\]',expr)
				for pair in param_pairs:
					attributes = pair.split(":")
					key = attributes[0]
					unit = attributes[1] 
					expr = expr.replace("[" + key + ":" + unit + "]", key)
					conversion_map.update({key:unit})
				
				param_no = 0
				for packet in packets:
					param = self._parameters[param_no];
					if param.get_id() in conversion_map:
						conversion_unit = conversion_map[param.get_id()]
					else:
						conversion_unit = None
					
					value = param.get_value(packet, conversion_unit);

					local_vars[param.get_id()] = float(value)
					param_no += 1
		
				try:
					value = eval(expr)
				except:
					value = 0.0

				format_tokens = value_format.split(".")
				output_format = "%.0f"
				if len(format_tokens) > 1:
					output_format = "%." + str(len(format_tokens[1])) + "f"

				value = output_format % value

		return value

	def get_value(self, packet, unit=None):
		value = ""
		
		if len(self._conversions) > 0 and unit == None:
			unit = self._conversions[0][0]
			
		for conversion in self._conversions:
			currunit = conversion[0]
			expr = conversion[1]
			value_format = conversion[2]
			if unit == currunit:
				# ignore 0xe8
				index = 1
				x = 0
				value_bytes = packet.get_data()[index:index + self._address_length]
				if self._address_length == 1:
					x = value_bytes[0]

				if self._address_length == 2:
					x = (value_bytes[0] << 8) | value_bytes[1]
				
				x = float(x)
				
				try:
					value = eval(expr)
				except:
					value = 0.0
					
				format_tokens = value_format.split(".")
				output_format = "%.0f"
				if len(format_tokens) > 1:
					output_format = "%." + str(len(format_tokens[1])) + "f"

				value = output_format % value
				
		return value
	
	def get_default_unit(self):
		if len(self._conversions) > 0:
			return self._conversions[0][0]
		return ""
	
	def is_supported(self, data):
		if self._byte_index != "none" and self._bit_index != "none" and len(data) > self._byte_index:
			cubyte = data[self._byte_index]
			bitmask = 1 << self._bit_index
			return cubyte & bitmask == bitmask
		else:
			return False

	def to_string(self):
		return "Param: id=" + self._id + ", name=" + self._name + ", desc=" + self._desc + ", byte=" + str(self._byte_index) + \
		", bit=" + str(self._bit_index) + ", target=" + str(self._target) + ", conversions=" + '[%s]' % ', '.join(map(str, self._conversions)) + \
		", address=" + hex(self._address) + "[" + str(self._address_length) + "]" 
