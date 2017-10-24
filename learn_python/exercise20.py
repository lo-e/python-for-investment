# -- coding: utf8 --

#从sys模组导入参数
from sys import argv
#定义函数，打印所有文件内容
def print_all(the_file):
	print the_file.read()
#定义函数，文件读取倒回到初始位置
def rewind(the_file):
	the_file.seek(0)
#定义函数，读取一行文件
def print_a_line(line_count, the_file):
	print 'content of line %r: %s' % (line_count, the_file.readline())
#解包，获得文件名
script, file_name = argv
#打开文件
the_file = open(file_name)
#显示打印全部文件内容
print "First let's print the whole file:"
#调用函数，打印全部文件内容
print_all(the_file)
#显示倒回到文件读取的初始位置
print "Now let's rewind, kind of like a tape."
#调用函数，倒回
rewind(the_file)
#显示逐行打印文件
print "Let's print the lines.:"
#从第一行打印文件内容
line_count = 1
print_a_line(line_count, the_file)
#行数增加一行，打印下一行文件内容
line_count += 1
print_a_line(line_count, the_file)
#行数增加一行，打印下一行文件内容
line_count += 1
print_a_line(line_count, the_file)