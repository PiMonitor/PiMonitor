'''
Created on 22-04-2013

@author: citan
'''

import platform

class PM(object):
	
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(PM, cls).__new__(cls, *args, **kwargs)
		return cls._instance
		
	def __init__(self):
		pass
		
	def set(self, log):
		self._log = log
	
	@classmethod
	def log(cls, message, mid=0):
		return PM().log_impl(message, mid)
	
	def log_impl(self, message, mid):
		return self._log(message, mid)

	def in_demo(self):
		return False