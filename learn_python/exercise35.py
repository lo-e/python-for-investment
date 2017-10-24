# -- coding: utf8 --

from sys import exit

#定义函数gold_room
def gold_room():
	print 'This room is full of gold. How much do you take?'
	#提示玩家输入
	next = raw_input('>')
	#这个蠢方法判断输入内容是否是数字
	if '0' in next or '1' in next:
		#给变量赋值
		how_much = int(next)
	else:
		#game over游戏结束
		dead('Man, learn to type a number.')
	#判断how_much是否小于50
	if how_much < 50:
		#胜利，游戏结束
		print "Nice, you're not greedy, you win!"
		exit(0)
	else:
		#game over游戏结束
		dead('You greedy bastard!')
#定义函数
def bear_room():
	print "There is a bear here."
	print "The bear has a bunch of honey."
	print "The fat bear is in front of another door."
	print "How are you going to move the bear?"
	#给变量赋值，初始状态熊没有移动
	bear_moved = False
	#进入循环模式
	while True:
		#提示输入
		next = raw_input('>')

		if next == 'take honey':
			#输入内容是'take honey'，game over游戏结束
			dead('The bear looks at you then slaps your face off.')
		elif next == 'taunt bear' and not bear_moved:
			#输入内容是'taunt bear'，熊开始移动
			print 'The bear has moved from the door, You can go through it now.'
			bear_moved = True
		elif next == 'taunt bear' and bear_moved:
			#熊移动后输入内容是'taunt bear'，game over游戏结束
			dead('The bear gets pissed off and chews your legs off.')
		elif next ==  'open door' and bear_moved:
			#熊移动后输入内容是'open door'，进入游戏下一阶段
			gold_room()
		else:
			#输入其它内容无效
			print 'I got no idea what that means.'

def cthulhu_room():
	print 'Here you see the great evil Cthulhu.'
	print 'He, it, whatever stares at you and you go insane.'
	print 'Do you flee your life or eat your head?'
	#提示输入
	next = raw_input('>')

	if 'flee' in next:
		#输入内容是'flee'，从新开始游戏
		start()
	elif 'head' in next:
		#输入内容是'head'，game over游戏结束
		dead('Well, that was tasty!')
	else:
		#输入其它内容无效
		cthulhu_room()

#定义函数
def dead(why):
	#game over游戏结束，显示结果
	print why, 'Good job!'
	#退出脚本
	exit(0)

#定义函数
def start():
	print 'You are in a dark room.'
	print 'There is a door to your right and left.'
	print 'Which one do you take?'
	#提示输入
	next = raw_input('>')

	if 'left' in next:
		#输入内容是'left'，进入游戏下一阶段bear_room
		bear_room()
	elif 'right' in next:
		#输入内容是'right'，进入游戏下一阶段cthulhu_room
		cthulhu_room()
	else:
		#输入其它内容，game over游戏结束
		dead('You stumble around the room until you starve.')

#开始游戏
start()