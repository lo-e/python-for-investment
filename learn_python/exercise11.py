# -- coding: utf8 --

#提问年龄
print 'How old are you?', 
#要求输入年龄
age = raw_input()
#提问身高
print 'How tall are you?', 
#要求输入身高
height = raw_input()
#提问体重
print 'How much do you weigh?', 
#要求输入体重
weight = raw_input()

#显示所有问答结果
print "So,you'er %s old, %s tall and %s heavy." % (age,height,weight)