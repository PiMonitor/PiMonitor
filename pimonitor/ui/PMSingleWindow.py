'''
Created on 22-04-2013

@author: citan
'''

import pygame

class PMSingleWindow(object):
	'''
	classdocs
	'''
	
	def __init__(self, param):
		self._fg_color = pygame.Color(230, 166, 0)
		self._fg_color_dim = pygame.Color(200, 140, 0)
		self._bg_color = pygame.Color(0, 0, 0)
		self._param = param
		self._packets = None
		
		self._x_offset = 0
		
	def set_surface(self, surface):
		if surface == None:
			return

		self._surface = surface
		self._width = self._surface.get_width();
		self._height = self._surface.get_height();

		self._title_font_size = int(self._surface.get_height() / 9)
		self._value_font_size = int(self._surface.get_height() / 1.8)
		self._unit_font_size = int(self._surface.get_height() / 4)
		
		self._title_font = pygame.font.SysFont(pygame.font.get_default_font(), self._title_font_size)
		self._value_font = pygame.font.SysFont(pygame.font.get_default_font(), self._value_font_size)
		self._unit_font = pygame.font.SysFont(pygame.font.get_default_font(), self._unit_font_size)
		
		self._font_aa = 1

		self._title_lbl = self._title_font.render(self._param.get_name(), self._font_aa, self._fg_color)
		
		value_lbl_width = self._value_font.render("-000.0", self._font_aa, self._fg_color).get_width()
		self._x_offset = (self._width - value_lbl_width) / 2
		
		self._unit_lbl = self._unit_font.render(self._param.get_default_unit(), self._font_aa, self._fg_color_dim)
		self._end_x_offset = self._width - self._unit_lbl.get_width() - 10 
	
	def render(self):
		if self._packets != None:
			if self._param.get_address_length() > 0:
				value = self._param.get_value(self._packets[0])
			elif self._param.get_dependencies():
				value = self._param.get_calculated_value(self._packets)
		else:
			value = "??"
				
		value_lbl = self._value_font.render(value, self._font_aa, self._fg_color)
		
		self._surface.blit(self._title_lbl, (2, 2))
		self._surface.blit(value_lbl, (self._x_offset, 10 + self._title_font_size))
		self._surface.blit(self._unit_lbl, (self._end_x_offset, 10 + self._title_font_size + self._value_font_size))
		
	def set_packets(self, packets):
		self._packets = packets
		
	def get_parameter(self):
		return self._param
		
		