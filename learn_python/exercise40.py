# -- coding: utf8 --

#给字典citiesd赋值
cities = {'CA':'San Francisco', 'MI':'Detroit', 'FL':'Jacksonville'}
cities['NY'] = 'New York'
cities['OR'] = 'Portland'
#定义函数
def find_city(themap, state):
	#判断state是否是themap中所有key的其中之一
	if state in themap:
		return themap[state]
	else:
		return 'not found!'
#将函数find_city添加到字典cities
cities['find'] = find_city
#开始循环
while True:
	#提示输入
	print 'State? (ENTER to quit)'
	state = raw_input('>')

	if not state:
		#如果直接回车说明没有输入任何内容，终止循环
		break
	#显示函数find_city的处理结果
	print cities['find'](cities, state)