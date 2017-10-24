# -- coding: utf8 --

from random import randint

#定义超能怪兽
class monster_a(object):
	"""docstring for monster_a"""
	def __init__(self, enemy):
		super(monster_a, self).__init__()
		#超能怪兽有三个属性：1、敌人  2、能量  3、怪兽名称
		self.enemy = enemy
		self.power = 1
		self.name = 'monster_a'

	def fight(self):
		#开始战斗
		#敌人将损失能量
		self.enemy.energy -= self.power
		#敌人的能量最少将全部失去
		if self.enemy.energy <= 0:
			self.enemy.energy = 0
		#返回下一个战斗的怪兽索引值
		return randint(0,self.enemy.enemy_count-1)
