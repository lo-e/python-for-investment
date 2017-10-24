# -- coding: utf8 --

#从sys模组导入参数
from sys import argv
#将参数解包
script, name = argv
#提示符，用变量作为提示符方便统一修改
prompt = '> '
#打印一段文字（包含解包出来的脚本名称和用户名称）
print """
Hi %s, I'm the %s script
I'd like to ask you a few questions.
Do you like me %s""" % (name, script, name)
#提示用户输入是否喜欢我
likes = raw_input(prompt)
#提问用户住在哪儿
print 'Where do you live %s?' % name
#提示用户输入居住地
living = raw_input(prompt)
#提问用户用的什么电脑
print 'What kind of computer do you have %s?' % name
#提示用户输入电脑信息
computer = raw_input(prompt)
#显示经过语言组织过的用户输入的所有结果
print """\n\nAlright, so you said %r about liking me.
You live in %r.Not sure where that is.
And you have a %r computer. Nice.""" % (likes, living, computer)