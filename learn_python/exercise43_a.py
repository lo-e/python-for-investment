# -- coding: utf8 --

#定义游戏大魔王
class Devil(object):
	"""docstring for animal_a"""
	def __init__(self, energy, enemy_count):
		super(Devil, self).__init__()
		#大魔王有两个属性：1、能量  2、敌人数量
		self.energy = energy
		self.enemy_count = enemy_count