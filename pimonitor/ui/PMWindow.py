'''
Created on 22-04-2013

@author: citan
'''

import pygame

class PMWindow(object):
	'''
	classdocs
	'''
	
	def __init__(self):
		self._fg_color = pygame.Color(255, 255, 255)
		self._bg_color = pygame.Color(0, 0, 0)
		self._dict = dict()
		
		# P60 Gear position
		# P97 Transfer Duty Ratio
		# P96 Lock Up Duty Ratio
		# P122 Oil Temperature
		# P104 ATF Temperature
		self._pids = ["P60", "P97", "P96", "P122", "P104"]
		
	def set_surface(self, surface):
		self._surface = surface
		self._width = self._surface.get_width();
		self._height = self._surface.get_height();

		self._title_font_size = int(self._surface.get_height() / 16)
		self._value_font_size = int(self._surface.get_height() / 3)
		self._title_font = pygame.font.SysFont(pygame.font.get_default_font(), self._title_font_size)
		self._value_font = pygame.font.SysFont(pygame.font.get_default_font(), self._value_font_size)

		self._font_aa = 1
		
		self._value_lbl_width = self._value_font.render("999", self._font_aa, self._fg_color).get_width()
		
	
	def render(self):
		
		first_row_height = self._title_font_size + self._value_font_size + 10
		second_row_height = first_row_height + self._title_font_size + self._value_font_size + 20
		pygame.draw.line(self._surface, self._fg_color, (0, first_row_height + 10), (self._width, first_row_height + 10))

		for param, value in self._dict.iteritems():
			title = param.get_name() #+ " (" + param.get_default_unit() + ")"
			
			
			first_row_ids = ["P60", "P122", "P104"]
			if param.get_id() in first_row_ids:
				index = first_row_ids.index(param.get_id())
				x_offset = (self._width / len(first_row_ids)) * index + 10
				
				titlelbl = self._title_font.render(title, self._font_aa, self._fg_color)
				valuelbl = self._value_font.render(value, self._font_aa, self._fg_color)
				self._surface.blit(titlelbl, (x_offset + 10, 10))
				self._surface.blit(valuelbl, (x_offset + 10, 10 + self._title_font_size))

				pygame.draw.line(self._surface, self._fg_color, (x_offset, 0), (x_offset, first_row_height))
			
			second_row_ids = ["P97", "P96"]
			
			if param.get_id() in second_row_ids:
				index = second_row_ids.index(param.get_id())
				x_offset = (self._width / len(second_row_ids)) * index + 10

				titlelbl = self._title_font.render(title, self._font_aa, self._fg_color)
				valuelbl = self._value_font.render(value, self._font_aa, self._fg_color)
				self._surface.blit(titlelbl, (x_offset + 10, first_row_height + 20))
				self._surface.blit(valuelbl, (x_offset + 10, first_row_height + 20 + self._title_font_size))
				
				pygame.draw.line(self._surface, self._fg_color, (x_offset, first_row_height + 20), (x_offset, second_row_height))
			
				x_offset += 10

	def get_pids(self):
		return self._pids 
	
	def set_value(self, param, packet):
		self._dict[param] = param.get_value(packet)
		