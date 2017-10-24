# -- coding: utf8 --
#从模组sys导入参数
from sys import argv
#将参数解包
script, file_name = argv
#打开文件
the_file = open(file_name)
#读取文件
file_read = the_file.read()
#关闭文件（读取文件后就可以关闭了，不会影响read_file的值，切记要将打开的文件关闭，不要问为什么）
the_file.close()
#显示文件内容
print "Here's your file %r:\n%s" % (file_name, file_read)
#显示再次输入文件
print "Type the file again:"
#提示再次输入文件
new_file_name = raw_input('> ')
#打开新文件
new_file = open(new_file_name)
#读取新文件
file_read = new_file.read()
#关闭新文件（不会再次强调了）
new_file.close()
#显示刚打开的新文件内容
print file_read

