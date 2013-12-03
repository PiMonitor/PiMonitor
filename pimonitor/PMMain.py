# -*- coding: utf-8 -*-

'''
Created on 29-03-2013

@author: citan
'''

import array
import os
import os.path
import time
import cPickle as pickle

from pimonitor.PM import PM
from pimonitor.PMConnection import PMConnection
from pimonitor.PMDemoConnection import PMDemoConnection
from pimonitor.PMPacket import PMPacket
from pimonitor.PMParameter import PMParameter
from pimonitor.PMUtils import PMUtils
from pimonitor.PMXmlParser import PMXmlParser

from pimonitor.ui.PMScreen import PMScreen
from pimonitor.ui.PMSingleWindow import PMSingleWindow

if __name__ == '__main__':

	from evdev import InputDevice, list_devices
	devices = map(InputDevice, list_devices())
	eventX = ""
	for dev in devices:
			if dev.name == "ADS7846 Touchscreen":
				eventX = dev.fn

	os.environ["SDL_FBDEV"] = "/dev/fb1"
	os.environ["SDL_MOUSEDRV"] = "TSLIB"
	os.environ["SDL_MOUSEDEV"] = eventX

	screen = PMScreen()
	log_id = PM.log('Application started')
	
	screen.render()
	
	parser = PMXmlParser();

	supported_parameters = []
	
	if os.path.isfile("data/data.pkl"):
		input = open("data/data.pkl", "rb")
		defined_parameters = pickle.load(input)
		input.close()
	else:
		defined_parameters = parser.parse("logger_METRIC_EN_v131.xml")
		output = open("data/data.pkl", "wb")
		pickle.dump(defined_parameters, output, -1)
		output.close()		

	connection = PMConnection()
	#connection = PMDemoConnection()
	while True:
		try:
			connection.open()
		
			ecu_packet = connection.init(1)
			tcu_packet = connection.init(2)
						
			if ecu_packet == None or tcu_packet == None:
				PM.log("Can't get initial data", log_id)
				continue;
			
			for p in defined_parameters:
				if (p.get_target() & 0x1 == 0x1) and p.is_supported(ecu_packet.to_bytes()[5:]):
					if not filter(lambda x: x.get_id() == p.get_id(), supported_parameters):
						supported_parameters.append(p)

			for p in defined_parameters:
				if ((p.get_target() & 0x2 == 0x2) or (p.get_target() & 0x1 == 0x1)) and p.is_supported(tcu_packet.to_bytes()[5:]):
					if not filter(lambda x: x.get_id() == p.get_id(), supported_parameters):
						supported_parameters.append(p)

			for p in defined_parameters:				
				p_deps = p.get_dependencies();
				if not p_deps:
					continue

				deps_found = () 
				for dep in p_deps:
					deps_found = filter(lambda x: x.get_id() == dep, supported_parameters)
					if not deps_found:
						break

					if len(deps_found) > 1:
						raise Exception('duplicated dependencies', deps_found) 
									
					p.add_parameter(deps_found[0])

				if deps_found: 
					supported_parameters.append(p) 					
				
			# each ID must be in a form P01 - first letter, then a number
			supported_parameters.sort(key=lambda p: int(p.get_id()[1:]), reverse=False)
			
			for p in supported_parameters:			
				window = PMSingleWindow(p)
				screen.add_window(window)

			while True:
				window = screen.get_window()
				param = window.get_parameter()
				parameters = param.get_parameters()
				if parameters:
					packets = connection.read_parameters(parameters)
					window.set_packets(packets)
				else:
					packet = connection.read_parameter(param)
					window.set_packets([packet])
				
				#ecu_response_packets = connection.read_parameters(ecu_params)
				#tcu_response_packets = connection.read_parameters(tcu_params)

				#param_no = 0
				#for ecu_packet in ecu_response_packets:
				#	param = ecu_params[param_no]
				#	window.set_value(param, ecu_packet)
				#	param_no += 1

				#param_no = 0
				#for tcu_packet in tcu_response_packets:
				#	param = tcu_params[param_no]
				#	window.set_value(param, tcu_packet)
				#	param_no += 1

				screen.render()

		except IOError as e:
			PM.log('I/O error: {0} {1}'.format(e.errno, e.strerror), log_id)
			if connection != None:
				connection.close()
				time.sleep(3)
			continue

	screen.close()
