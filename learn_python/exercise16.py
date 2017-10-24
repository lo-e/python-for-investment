# -- coding: utf8 --

#从sys模组导入参数
from sys import argv
#将参数解包
script, file_name = argv
#显示即将清空文件内容
print """we are going to erase %r.
If you don't want that, hit CTRL-C(^c).
If you do want that, hit RETURN."""
#提示是否同意清空文件内容
action = raw_input('?')
#显示正在打开文件
print 'opening the file...'
#打开文件
the_file = open(file_name, 'w')
#显示正在清空文件内容
print 'Truncating the file. Goodbye!'
#清空文件内容
the_file.truncate()
#显示将要用户输入内容
print "Now I'm going to ask you for three lines."
#提示用户输入内容
line1 = raw_input('line1 > ')
line2 = raw_input('line2 > ')
line3 = raw_input('line3 > ')
#显示即将将用户输入的内容写入文件
print "I'm going to write these to the file."
#将内容写入文件
the_file.write(line1)
the_file.write('\n')
the_file.write(line2)
the_file.write('\n')
the_file.write(line3)
#显示关闭文件
print 'And finally, we close it'
#关闭文件
the_file.close()