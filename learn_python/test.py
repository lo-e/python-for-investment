# -- coding: utf8 --

import exercise49
import sys
import os
import test1

class Cat(object):
	"""docstring for Cat"""
	a = 'yes yes'
	def __init__(self, name):
		super(Cat, self).__init__()
		self.name = name

class BlackCat(Cat):
	"""docstring for BlackCat"""
	def __init__(self, name, like):
		super(BlackCat, self).__init__(name)
		self.like = like

	def action(self):
		print self.name, self.like
		
		

the_cat = BlackCat('pika', 'food')
print the_cat.a
