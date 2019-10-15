#!/usr/bin/python3

# Standard library imports
import sys
from time import time
from math import sqrt

# Third party imports
import pygame
from pygame.locals import *
import numpy as np
from random import shuffle

# Local application imports
if len(sys.argv) > 1 and sys.argv[1] == 'test':
	import utilities.wbb_calitera as wbb
	from image import Image
	from screen import Screen
else:
	import src.utilities.wbb_calitera as wbb
	from src.image import Image
	from src.screen import Screen

# Global constants
LOS_SAMPLE = 200 	# LOS sample
DT = 0.04			# Period of acquisition
	
# centimeters = pixels * 2.54 / dpi

class Los():
	"""
	A class used to implement Limits of Stability

	Attributes
	----------
	wiimote : cwiid.Wiimote
		Wii Balance Board (WBB)
	calibrations : dict
		WBB calibrations

	Methods
	-------
	cop_to_pos
		Converts center of pressure (cop) to screen position
	get_mean
		Calculates the mean of center of pressure (cop)
	
	"""
	def __init__(self, wiimote, calibrations, cop, resolution):
		self.__wiimote = wiimote
		self.__calibrations = calibrations
		self.__screen = Screen(resolution)
		self.__display = pygame.display.set_mode(self.screen.res, self.screen.opt)
		pygame.display.set_caption('Limits of Stability')
		self.__sprites = {
			'ball' : 	Image('media/ball.png'), 	# Target
			'cur_pos' : Image('media/target.png'), 	# Current position
		}
		self.__line = {
			'color' : (150,150,150),
			'darker_color' : (0,0,255),
			'width' : int(self.screen.width * 0.007)
		}

		self.__line_pos = [self.screen.middle_top, self.screen.right_top, self.screen.right_middle, self.screen.right_bottom, self.screen.middle_bottom, self.screen.left_bottom, self.screen.left_middle, self.screen.left_top, self.screen.middle]

		center = self.screen.width_middle-self.__sprites['ball'].rect[2]//2
		cateto = center // sqrt(2)
		diag_left_top = (center - cateto, center - cateto)
		diag_right_top = (center + cateto, center - cateto)
		diag_left_bottom = (center - cateto, center + cateto)
		diag_right_bottom = (center + cateto, center + cateto)

		self.__circle_pos = [(center, 0), diag_right_top, (center*2, center), diag_right_bottom, (center, center *2), diag_left_bottom, (0, center), diag_left_top, (center, center)]

		self.__current_pos = list(range(8))
		shuffle(self.__current_pos)
		self.__current_pos = self.outersperse(self.__current_pos, 8)
		
		self.__cop = cop
		self.__t = time()

		# Shows Los Screen
		self.__display.fill(self.screen.bg_color)
		for k in range(8):
			pygame.draw.line(self.__display, self.__line['color'], self.__line_pos[k], (self.screen.width_middle,self.screen.height_middle), self.__line['width'])
		self.__display.blit(self.__sprites['ball'].img, (center, center))
		self.__display.blit(self.__sprites['cur_pos'].img, (self.screen.width_middle - self.__sprites['cur_pos'].rect[2]//2, self.screen.height_middle - self.__sprites['cur_pos'].rect[3]//2))
		pygame.display.flip()

		self.__x_med, self.__y_med = self.get_mean(self.wiimote, self.calibrations, LOS_SAMPLE//2, DT)

	@property
	def screen(self):
		"""This is screen property"""
		return self.__screen

	@property
	def wiimote(self):
		"""This is wiimote property"""
		return self.__wiimote

	@property
	def calibrations(self):
		"""This is calibrations property"""
		return self.__calibrations

	def cop_to_pos(self, x, y, x_med = 0, y_med = 0):
		'''Converts center of pressure (cop) to screen position

		Parameters
		----------
		x: float
			cop position on wiimote x-axis 
		y: float
			cop position on wiimote y-axis

		Returns
		-------
		tuple
			cop position on the screen 
		'''
		X = 433 / 2 # mm
		Y = -1 * 238 / 2 # mm

		xpos = (( x - x_med ) / X ) * self.screen.width_middle + self.screen.width_middle
		ypos = (( y + y_med ) / Y ) * self.screen.height_middle + self.screen.height_middle

		return (xpos, ypos)

	def get_mean(self, wiimote, calibrations, sample, dt):
		'''Calculates the mean of center of pressure (cop)

		Parameters
		----------
		wiimote : cwiid.Wiimote
			The plataform
		calibrations : dict
			Platform calibrations
		sample : int
			Sample size
		dt : float
			Frequency of acquisition

		Returns
		-------
		tuple
			mean of the center of pressure
		'''

		# CoP mean
		x_med = np.zeros(sample)
		y_med = np.zeros(sample)
		t = time()
		for i in range(sample):
			readings = wbb.captura1(wiimote)
			x_med[i], y_med[i] = wbb.calCoP(readings, calibrations, wbb.escala_eu)
			while time() < t + dt:
				pass
			else:
				t += dt
		x_med = x_med.mean()
		y_med = x_med.mean()

		return (x_med, y_med)

	def outersperse(self, lst, item):
		"""
		Inserts a item at head, tail and between each list element

		Parameters
		----------
		lst: list
			The list
		item: any
			The item to be outerspersed
		
		Returns
		-------
		list
			The list outerpersed with item
		"""

		result = [item] * (len(lst) * 2 + 1)
		result[1::2] = lst
		return result

	def intersperse(self, lst, item):
		"""
		Inserts a item between each list element

		Parameters
		----------
		lst: list
			The list
		item: any
			The item to be interspersed
		
		Returns
		-------
		list
			The list interpersed with item
		"""
		
		result = [item] * (len(lst) * 2 - 1)
		result[0::2] = lst
		return result

	def main(self):
		global LOS_SAMPLE, DT
		for cp in self.__current_pos:
			if cp == 8:	# If the target is at screen center
				sample = LOS_SAMPLE // 2
			else:
				sample = LOS_SAMPLE
			for j in range(sample):
				for event in pygame.event.get():
					if event.type == KEYDOWN:
						if event.key == K_ESCAPE:
							pygame.quit()

				# Gets wbb readings
				readings = wbb.captura1(self.wiimote)
				
				# Gets CoP
				x_balance, y_balance = wbb.calCoP(readings, self.calibrations, wbb.escala_eu)

				if cp != 8:
					# Assigns CoP values to the matrices 
					self.__cop[cp][j] = x_balance, y_balance

				# Converts cop to screen pos
				xpos, ypos = self.cop_to_pos(x_balance, y_balance, self.__x_med, self.__y_med)
				
				# Blanks the screen
				self.__display.fill(self.screen.bg_color)
				
				pygame.draw.circle(self.__display, (210,210,210), self.screen.middle, 330)

				# Draws LOS lines
				for k in range(8):
					pygame.draw.line(self.__display, self.__line['color'], self.__line_pos[k], (self.screen.width_middle,self.screen.height_middle), self.__line['width'])
				pygame.draw.line(self.__display, self.__line['darker_color'], self.__line_pos[cp], (self.screen.width_middle,self.screen.height_middle), self.__line['width'])

				# Sets target and current pos 
				self.__sprites['cur_pos'].x, self.__sprites['cur_pos'].y = xpos, ypos
				self.__sprites['ball'].x, self.__sprites['ball'].y = self.__circle_pos[cp][0], self.__circle_pos[cp][1]

				# Blits target and current pos 
				self.__display.blit(self.__sprites['ball'].img, (self.__sprites['ball'].x, self.__sprites['ball'].y))
				try:
					self.__display.blit(self.__sprites['cur_pos'].img, (int(self.__sprites['cur_pos'].x), int(self.__sprites['cur_pos'].y)))
				except ValueError:
					self.__display.blit(self.__sprites['cur_pos'].img, (self.screen.width_middle - self.__sprites['cur_pos'].rect[2]//2, self.screen.height_middle - self.__sprites['cur_pos'].rect[3]//2))
				pygame.display.flip()

				# Delay
				while time() < self.__t + DT:
					pass
				else:
					self.__t += DT

		return self.__cop, (self.__x_med, self.__y_med)
		pygame.quit()

if __name__ == "__main__":
	# Platform connection
	
	# wiimote, battery = conecta('00 :26:59:DD:0A:6F')
	# self.calibration = {'right_top': [2319.0, 4249.2863977227562, 6123.3200972029945],
	#                    'right_bottom': [3005.0, 4932.535439819314, 6894.5571308433591],
	#                    'left_top': [4161.0, 6082.8245392950312, 7974.3120731868639],
	#                    'left_bottom': [4039.0, 6051.2591790830556, 8075.457648501033]}

	wiimote = wbb.conecta('00:23:CC:36:BB:FB')
	calibrations = {'right_top': [15997.098, 18100.139752805848, 19899.986639971234],
				'right_bottom': [15918.538, 18058.25096456056, 19770.919367546234],
				'left_top': [8381.506, 10418.473898934291, 12209.380344709283],
				'left_bottom': [18023.66, 20173.535248689008, 21844.79971434051]}
	
	# wiimote = wbb.conecta('00:22:4C:56:D3:F4')
	# calibrations = {'right_top': [5129.0, 7000.2527202635247, 8673.753146324183],
	# 			'right_bottom': [19824.0, 21776.951434339429, 23546.832586428671],
	# 			'left_top': [2371.0, 4268.7978532247189, 5983.5125723310794],
	# 			'left_bottom': [17340.0, 19136.878015404596, 20761.645463499703]}

	np.set_printoptions(threshold=np.inf)
	cop = np.zeros((8, LOS_SAMPLE), dtype=(float, 2))
	los = Los(wiimote, calibrations, cop, 1366)
	los.main()