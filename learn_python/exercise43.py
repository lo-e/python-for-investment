# -- coding: utf8 --

from exercise_43_a import Devil
from exercise_43_b import monster_a
from exercise_43_c import monster_b
from exercise_43_d import monster_c
from sys import exit
from random import randint

#定义游戏
class Game(object):
	"""docstring for Game"""
	def __init__(self, devil, monsters):
		super(Game, self).__init__()
		#游戏有三个基本属性：1、大魔王  2、怪兽  3、分数
		self.devil = devil
		self.monsters = monsters
		self.score = 6

	def begin(self):
		#开始游戏
		#游戏的成就
		self.achievement = []
		#开始随意指定一个怪兽索引
		next = randint(0, len(self.monsters)-1)
		while True:
			#找到该索引的怪兽
			monster = self.monsters[next]
			#怪兽开始战斗，并且准备好下一次战斗的怪兽索引
			next = monster.fight()
			#一场战斗结束后获得的成就
			self.achievement.append('%s:%d' % (monster.name, monster.power))
			#自身将损耗生命值
			self.score -= 1

			if self.devil.energy <= 0:
				#大魔王能量被消灭了，战斗胜利，显示剩余生命力和获得的成就
				print 'You win!'
				print 'score:%d' % self.score
				achievement = ' '.join(self.achievement)
				print 'achievement:%s' % achievement
				exit()
			if self.score <= 0:
				#生命力消耗殆尽，大魔王还没有被消灭，战斗失败，显示剩余生命力和获得的成就
				print 'Game over..You die'
				print 'score:%d' % self.score
				achievement = ' '.join(self.achievement)
				print 'achievement:%s' % achievement
				exit()

#创建大魔王和即将征战沙场的怪兽们
the_devil = Devil(10, 3)
monster1 = monster_a(the_devil)
monster2 = monster_b(the_devil)
monster3 = monster_c(the_devil)
monsters = [monster1, monster2, monster3]
#创建游戏，用以上创建的大魔王和怪兽们初始化
the_game = Game(the_devil, monsters)
#提示确认开始游戏
raw_input('ENTER to begin > ')
#开始战斗
the_game.begin()

