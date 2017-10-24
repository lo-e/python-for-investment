# -- coding: utf8 --

#从sys模组导入参数
from sys import argv
#从os.path模组导入exists功能
from os.path import exists
#将参数解包
script, from_file_name, to_file_name = argv
#显示将要拷贝文件内容到另一个文件
print 'Copying from %s to %s' % (from_file_name, to_file_name)
#打开from文件
from_file = open(from_file_name)
#读取from文件
from_file_read = from_file.read()
#获得from内容大小
from_file_len = len(from_file_read)
#显示from文件内容大小
print 'The input file is %r bytes long' % from_file_len
#关闭from文件
from_file.close()
#显示to文件是否在当前目录存在
print 'Dose the output file exist? %r' % exists(to_file_name)
#显示让用户确认是否同意执行拷贝内容
print 'Ready, hit RETURN to continue, CTRL-C(^c) to abort'
#提示用户确认
raw_input()
#打开to文件
to_file = open(to_file_name, 'w')
#清空to文件
to_file.truncate()
#内容写入to文件
to_file.write(from_file_read)
#关闭to文件
to_file.close()
#显示结束
print 'Alright all done'