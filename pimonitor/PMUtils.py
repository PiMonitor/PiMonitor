'''
Created on 13-04-2013

@author: citan
'''

import os
from pimonitor.PM import PM

class PMUtils(object):
	'''
	classdocs
	'''

	
	# Return CPU temperature as a character string
	@classmethod    
	def get_cpu_temperature(cls):
		res = os.popen('vcgencmd measure_temp').readline()
		return(res.replace("temp=", "").replace("'C\n", ""))

	# Return RAM information (unit=kb) in a list                                        
	# Index 0: total RAM                                                                
	# Index 1: used RAM                                                                 
	# Index 2: free RAM
	@classmethod                                                                 
	def get_ram_info(cls):
		p = os.popen('free')
		i = 0
		while 1:
			i = i + 1
			line = p.readline()
			if i == 2:
				return(line.split()[1:4])

	# Return % of CPU used by user as a character string
	@classmethod                                
	def get_cpu_use(cls):
		return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))

	# Return information about disk space as a list (unit included)                     
	# Index 0: total disk space                                                         
	# Index 1: used disk space                                                          
	# Index 2: remaining disk space                                                     
	# Index 3: percentage of disk used
	@classmethod                                                  
	def get_disk_space(cls):
		p = os.popen("df -h /")
		i = 0
		while 1:
			i = i + 1
			line = p.readline()
			if i == 2:
				return(line.split()[1:5])

	@classmethod
	def log_os_stats(cls):
		try:
			cpu_temp = PMUtils.get_cpu_temperature()
			if len(cpu_temp) > 0:
				PM.log("CPU temp: " + cpu_temp)
				
			ram_stats = PMUtils.get_ram_info()
			if len(ram_stats) == 3:
				ram_free = round(int(ram_stats[2]) / 1000,1)
				PM.log("RAM free: " + str(ram_free))
				
			cpu_usage = PMUtils.get_cpu_use()
			if len(cpu_usage) > 0:
				PM.log("CPU usage: " + str(cpu_usage))
				
		except IOError:
			pass