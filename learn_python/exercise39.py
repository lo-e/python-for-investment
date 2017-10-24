# -- coding: utf8 --

#给字符串变量赋值
sentence = 'Apples Organges Crows Telephone Light Sugar'
print "Wait there's not 10 things in that list, let's fix that."
#将字符串sentence用空格拆分并赋值给数组stuff
stuff = sentence.split(' ')
#给数组变量赋值
more_stuff = ['Day', 'Night', 'Song', 'Frisbee', 'Corn', 'Banana', 'Girl', 'Boy']
#当数组stuff的元素个数没有达到10时，持续循环
while len(stuff) != 10:
	#数组去除最后一个元素，并且赋值给next_one
	next_one = more_stuff.pop()
	#将next_one添加到数组stuff
	print 'Adding:', next_one
	stuff.append(next_one)
	#显示当前数组stuff的元素总数
	print "There's %d items now." % len(stuff)
#显示stuff所有元素值
print 'There we go:', stuff
print "Let's do some things with stuff."
#显示第二个元素
print stuff[1]
#显示最后一个元素
print stuff[-1]
#去除最后一个元素并显示
print stuff.pop()
#用' '空格将stuff所有元素连接成字符串
print ' '.join(stuff)
#用'#'将stuff对应元素连接成字符串
print '#'.join(stuff[3:5])

