# Third party imports
import pygame

class Image():
	'''A class used to represent a image

		Attributes
		----------
		file: str
			Image path
	'''
	def __init__(self, file):
		self.img = pygame.image.load(file)
		self.rect = list(self.img.get_rect())
		self.x = 0
		self.y = 0