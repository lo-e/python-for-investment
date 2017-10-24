# -- coding: utf8 --

#给预设的词汇赋值归类
directions = ['north', 'south', 'east', 'west', 'down', 'up', 'left', 'right', 'back']
verbs = ['go', 'stop', 'kill', 'eat']
stops = ['the', 'in', 'of', 'from', 'at', 'it']
nouns = ['door', 'bear', 'princess', 'cabinet']
#定义函数，进行内容归类处理
def scan(sentence):
	words = sentence.split()
	result = []
	for word in words:
		if word in directions:
			result.append(('direction', word))
		elif word in verbs:
			result.append(('verb', word))
		elif word in stops:
			result.append(('stop', word))
		elif word in nouns:
			result.append(('noun', word))
		elif number(word):
			result.append(('number', word))
		else:
			result.append(('error', word))

	return result
#定义函数，判断内容是否是整型数字
def number(word):
	try:
		number = int(word)
	except:
		return False
	else:
		return True

def engine():
	#开始循环
	while True:
		#显示直接回车可以退出
		print 'ENTER to exit'
		#提示输入内容
		sentence = raw_input('> ')
		#判断回车则退出
		if not sentence:
			exit()
		#显示处理分类后的结果
		print scan(sentence)

#engine()
