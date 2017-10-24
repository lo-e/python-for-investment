# -- coding: utf8 --

#导入模组exit，需要时退出程序
from sys import exit
#导入模组randint，这是个随机生成整型参数的函数
from random import randint

#定义函数
def death():
	#配置可能显示的文案
	quips = ['You died. You kinda suck at this.',
			 'Nice job, you died ...jackass.',
			 'Such a luser.',
			 "I have a small puppy that's better at this."]
	#随机显示不同的文案
	print quips[randint(0, len(quips)-1)]
	#退出程序
	exit(0)

#定义函数
def central_corridor():
	print 'You are in the central corridor.'
	#提示输入
	action = raw_input('> ')

	if action == 'shoot!':
		#输入内容不正确，游戏结束
		print 'You die'
		return'death'
	elif action == 'dodge!':
		#输入内容不正确，游戏结束
		print 'You die'
		return'death'
	elif action == 'tell a joke':
		#输入内容正确，进入游戏下一关卡
		print 'You go to laser weapon armory'
		return 'laser_weapon_armory'
	else:
		#无法识别的内容，重新输入
		print 'DOSE NOT COMPUTE!'
		return 'central_corridor'

#定义函数
def laser_weapon_armory():
	print 'You are in the laser weapon armory.'
	#随机产生三个整型组成字符串
	code = '%d%d%d' % (randint(1, 9), randint(1, 9), randint(1, 9))
	#提示输入一串数字
	guess = raw_input('[keypad]> ')

	guesses = 0
	#循环条件，输入内容和code一样退出，输入次数达到10次退出
	while guess != code and guesses < 10:
		print 'BZZZZEDDD!'
		#循环索引加一
		guesses += 1
		#提示输入一串数字
		guess = raw_input('[keypad]> ')

	if guess == code:
		#如果输入的内容和code一样，进入游戏下一关卡
		print 'You go to the bridge.'
		return 'the_bridge'
	else:
		#其它情况，游戏结束
		print 'You die'
		return'death'

#定义函数
def the_bridge():
	print 'You are in the bridge.'
	#提示输入
	action = raw_input('> ')

	if action == 'throw the bomb':
		#如果这样的输入内容，游戏结束
		print 'You die'
		return'death'
	elif action == 'slowly place the bomb':
		#如果这样的输入内容，游戏进入下一关卡
		print 'You go to the escape pod.'
		return'escape pod'
	else:
		#如果输入其它内容，重新输入
		print 'DOSE NOT COMPUTE!'
		return 'the_bridge'

#定义函数
def escape_pod():
	print 'You are in the escape pod'
	#随机产生一个整型赋值给good_pod
	good_pod = randint(1,5)
	#提示输入
	guess = raw_input('[pod #]> ')

	if int(guess) != good_pod:
		#如果输入内容的整型不等于good_pod，游戏结束
		print 'You die.'
		return 'death'
	else:
		#其它情况，也就是输入的内容的整型等于good_pod，玩家胜利！
		print 'You win!'
		#退出程序
		exit(0)

#字典配置了所有游戏关卡
rooms = {'death':death,
		 'central_corridor':central_corridor,
		 'laser_weapon_armory':laser_weapon_armory,
		 'the_bridge':the_bridge,
		 'escape_pod':escape_pod}
#定义函数
def runner(dic, start):
	#开始的关卡
	next = start
	#进入循环
	while True:
		#关卡开始
		room = dic[next]
		next = room()

#开始游戏
#runner(rooms, 'central_corridor')

	


