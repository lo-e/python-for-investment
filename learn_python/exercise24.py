# -- coding: utf8 --

#显示说明
print "Let's practice everything."
#练习转义字符\的使用
print 'You\' need to know \'about escapes with \\ that do \n newlines and \t tabs.'
#练习'''的使用（'''还可以用"""替换）
poems = '''
\tThe lovely world
with logic so firmly planted
cannot discern \n the needs of love
nor comprehend passion from intuition
and requires an explanation
\n\twhere there is none.
'''
#显示刚刚那首美丽的诗句
print '------------------'
print poems
print '------------------'
#进行一个简单的计算
five = 10 - 2 + 3 - 6
print "This should be five: %s" % five
#定义一个函数，做一些基本的计算，返回三个参数
def secret_formula(started):
	jelly_beans = started * 500
	jars = jelly_beans / 1000
	crates = jars / 100
	return jelly_beans, jars, crates
#定义一个整型变量
start_point = 10000
#用刚刚定义的函数的返回值解包给三个变量，用上一行的变量作参数
jelly_beans, jars, crates = secret_formula(start_point)
print 'With a starting point of: %d' % start_point
print "We'd have %d beans, %d jars, %d crates." % (jelly_beans, jars, crates)
#换一种方式，用另一个初始变量值调用函数，并将返回值直接格式化打印
start_point = start_point / 10
print "We'd also do that this way:"
print "We'd have %d beans, %d jars, %d crates." % secret_formula(start_point)