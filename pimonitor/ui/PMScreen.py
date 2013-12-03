'''
Created on 18-04-2013

@author: citan
'''

import pygame
import os.path
import os
import sys

from pimonitor.PM import PM
from pimonitor.PMUtils import PMUtils

class PMScreen(object):
	'''
	classdocs
	'''
	LOG_FPS_EVENT = pygame.USEREVENT + 1
	LOG_STATS_EVENT = LOG_FPS_EVENT + 1
	ONE_SEC_EVENT = LOG_STATS_EVENT + 1
	 
	def __init__(self):
		'''
		Constructor
		'''
		pygame.init()
		pygame.mouse.set_visible(False)
		
		# seems to suit RPi
		self._color_depth = 16

		pygame.display.set_mode((0, 0), pygame.FULLSCREEN, self._color_depth)
		#pygame.display.set_mode((640, 480), 0, self._color_depth)
		self._surface = pygame.display.get_surface()

		self._clock = pygame.time.Clock()
		
		self._width = self._surface.get_width();
		self._height = self._surface.get_height();
		
		self._subwindow_alpha = 200
		
		self._font_size = int(self._height / 14)
		self._font = pygame.font.SysFont(pygame.font.get_default_font(), self._font_size)
		self._font_aa = 0
		self._fg_color = pygame.Color(255, 191, 0)
		self._bg_color = pygame.Color(0, 0, 0)
		self._dim_color = pygame.Color(200, 140, 0)
		
		self._log_lines = 4
		self._log_msg_id = 0
		self._log_surface = pygame.Surface((self._width / 2, self._font_size * self._log_lines), 0, self._color_depth)
		self._log_surface.set_alpha(self._subwindow_alpha)
		self._log_queue = []
		
		logger = PM()
		logger.set(self.log)
		
		self._fps_log_id = 0
		self._frame_no = 0
		self.load_resources()
		pygame.time.set_timer(PMScreen.LOG_FPS_EVENT, 10000)
		pygame.time.set_timer(PMScreen.LOG_STATS_EVENT, 30000)
		pygame.time.set_timer(PMScreen.ONE_SEC_EVENT, 1000)

		self._window = None
		self._windows = []
		
		self._pos_log_id = 0;
		self._mouse_down_pos = (0, 0);
		self._mouse_down_mark_timeout = 0
		
	def clear(self):
		self._surface.fill(self._bg_color)

	def load_resources(self):
		self._bg_img = pygame.image.load(os.path.join('res', 'subaru_logo.png')).convert()
		self._bg_img_rect = self._bg_img.get_rect()

	def render(self):
		self._clock.tick()
		
		for event in pygame.event.get():
			if event.type == PMScreen.LOG_FPS_EVENT:
				self._frame_no += 1
				self._fps_log_id = PM.log("FPS %.2f" % self._clock.get_fps(), self._fps_log_id)

			elif event.type == PMScreen.LOG_STATS_EVENT:
				PMUtils.log_os_stats()				
			elif event.type == pygame.QUIT:
				self.close()
				sys.exit()
			
			elif event.type == pygame.MOUSEBUTTONUP:
				self._mouse_down_mark_timeout = 0
				self._mouse_down_pos = pygame.mouse.get_pos();
				self._pos_log_id = PM.log('Mouse up at: %s/%s' % pygame.mouse.get_pos(), self._pos_log_id);
				if self._mouse_down_pos[0] < self._width / 2:
					self.prev_window()
				else:
					self.next_window()
			elif event.type == PMScreen.ONE_SEC_EVENT:
				self._mouse_down_mark_timeout += 1

		self.clear()
		
		if self._window == None:
			self.render_bg()

		if self._window != None:
			self._window.render()
			
		self.render_log()

		if self._mouse_down_mark_timeout < 2:
			pygame.draw.circle(self._surface, self._dim_color, self._mouse_down_pos, 16);
			
		pygame.display.update()

	def render_log(self):
		self.purge_logs()
		if len(self._log_queue) == 0:
			return
		
		self._log_surface.fill(self._bg_color)
		
		log_pos = 0
		for msg_entry in self._log_queue:
			msg_entry[2] = msg_entry[2] + 1
			message = msg_entry[1]
			message_lbl = self._font.render(message, self._font_aa, self._fg_color, self._bg_color)
			self._log_surface.blit(message_lbl, (0, log_pos))
			log_pos += self._font_size
		
		self._surface.blit(self._log_surface, (0, self._height - self._log_surface.get_height()))
		
	def render_bg(self):		
		#self._surface.blit(self._bg_img, self._bg_img_rect)
		pass

	def purge_oldest_log(self):
		oldest = pygame.time.get_ticks()
		
		for log_entry in self._log_queue:
			if log_entry[2] < oldest:
				oldest = log_entry[2]
				to_be_deleted = log_entry
				
		self._log_queue.remove(to_be_deleted)

		
	def purge_logs(self):
		to_be_deleted = []

		for log_entry in self._log_queue:
			if pygame.time.get_ticks() - log_entry[2] > 5000:
				to_be_deleted.append(log_entry)
			
		for log_entry in to_be_deleted:
			self._log_queue.remove(log_entry)

	def add_window(self, window):
		self._windows.append(window);
		if self._window == None:
			self.next_window()
		pass
	
	def set_window(self, window):
		if self._window != None:
			self._window.set_surface(None)
			
		self._window = window
		self._window.set_surface(self._surface)
	
	def get_window(self):
		return self._window
	
	def next_window(self):
		if not self._windows:
			return

		if self._window != None:
			index = self._windows.index(self._window)
		else:
			index = -1
			
		new_index = (index + 1) % len(self._windows)
		self.set_window(self._windows[new_index])
		self.log_window(new_index)
		
	def prev_window(self):
		if not self._windows:
			return
		
		if self._window != None:
			index = self._windows.index(self._window)
		else:
			index = 1
			
		new_index = (index - 1) % len(self._windows)		
		self.set_window(self._windows[new_index])
		self.log_window(new_index)
		
	def log_window(self, index):
		if self._window != None:
			PM.log(str(index + 1) + '/' + str(len(self._windows)) + ': ' + self._window.get_parameter().get_id(), 0)
		
	def log(self, message, mid):
		ticks = pygame.time.get_ticks()
		if mid == 0:
			self._log_msg_id = (self._log_msg_id % 1000) + 1
			mid = self._log_msg_id
		
		found = False
		for log_entry in self._log_queue:
			if log_entry[0] == mid:
				log_entry[1] = message
				found = True
				log_entry[2] = ticks

		self.purge_logs()
		
		# remove old messages if necessary
		if not found:
			if len(self._log_queue) >= self._log_lines :
				self.purge_oldest_log()
			self._log_queue.append([mid, message, ticks])
			
		self.render()
		
		return mid
	
	def close(self):
		pygame.display.quit()
