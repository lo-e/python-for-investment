# -- coding: utf8 --

#给变量i初始赋值
i = 0
#给数组变量numbers初始赋值空数组
numbers = []
#while循环条件i小于6
while i < 6:
	#显示当前i的值，并将i加入数组numbers
	print 'At the top i is %d' % i
	numbers.append(i)
	#i的值加一，并再次显示i的数值
	i += 1
	print 'At the bottom i is %d' % i
#用for循环遍历数组numbers显示数组内所有的值
print 'The numbers:'
for number in numbers:
	print number