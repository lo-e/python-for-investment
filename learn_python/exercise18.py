# -- coding: utf8 --

#定义函数，传一个包参数
def print_two(*args):
		arg1, arg2 = args
		print 'arg1:%r, arg2:%r' % (arg1, arg2)
#定义函数，传两个参数
def print_two_again(arg1, arg2):
		print 'arg1:%r, arg2:%r' % (arg1, arg2)
#定义函数，传一个参数
def print_one(argv):
		print 'argv:%r' % argv
#定义函数，不传参数
def print_none():
		print 'I got nothing'

print_two('abc', 'xyz')
print_two_again('abc', 'xyz')
print_one('abc')
print_none()