# -- coding: utf8 --

from collect import *

#定义函数，抛出异常
class ParseError(Exception):
	"""docstring for ParseError"""
	def __init__(self):
		super(ParseError, self).__init__()

#定义函数
class Sentence(object):
	"""docstring for Sentence"""
	def __init__(self, subject, verb, object):
		super(Sentence, self).__init__()
		#这些都是基本的英语语句结构
		self.subject = subject[1]
		self.verb = verb[1]
		self.object = object[1]

#定义类，所有的语句解析都在这里
class Parse(object):
	"""docstring for Parse"""
	def __init__(self):
		super(Parse, self).__init__()

	#定义函数
	def peek(self, word_list):
		#找到第一个元组所包含的单词类型，并返回
		if word_list:
			word = word_list[0]
			return word[0]
		else:
			return None

	#定义函数
	def match(self, word_list, expecting):
		if word_list:
			#抛出第一个元组
			word = word_list.pop(0)
			if  word[0] == expecting:
				#匹配正确，返回这个元组
				return word
			else:
				#匹配不成功
				return None
		else:
			return None

	#定义函数
	def skip(self, word_list, word_type):
		#排除匹配的元组
		while self.peek(word_list) == word_type:
			self.match(word_list, word_type)

	#定义函数
	def parse_verb(self, word_list):
		#先排除掉修饰词
		self.skip(word_list, 'stop')

		if self.peek(word_list) == 'verb':
			#匹配到动词
			return self.match(word_list, 'verb')
		else:
			#匹配不成功，抛出异常
			raise ParseError('Expected a verb next.')

	#定义函数
	def parse_object(self, word_list):
		#先排除掉修饰词
		self.skip(word_list, 'stop')
		#第一个单词的类型
		next = self.peek(word_list)
		if next == 'noun':
			#第一个单词是名词，匹配成功
			return self.match(word_list, 'noun')
		elif next == 'direction':
			#第一个单词表示方向，匹配成功
			return self.match(word_list, 'direction')
		else:
			#匹配不成功，抛出异常
			raise ParseError('Expected noun or direction next.')

	#定义函数
	def parse_subject(self, word_list, subj):
		#匹配谓语
		verb = self.parse_verb(word_list)
		#匹配主语
		obj = self.parse_object(word_list)
		#以上匹配都成功，生成句子并返回
		return Sentence(subj, verb, obj)

	#定义函数
	def parse_sentence(self, word_list):
		#先排除掉修饰词
		self.skip(word_list, 'stop')
		#找到第一个单词的类型
		start = self.peek(word_list)
		if start == 'noun':
			#第一个单词是名词，可以作为主语，匹配成功
			subject = self.match(word_list, 'noun')
			return self.parse_subject(word_list, subject)
		elif start == 'verb':
			#第一个但此时动词，可以作为谓语，默认'player'作为主语，匹配成功
			return self.parse_subject(word_list, ('noun', 'player'))
		else:
			#否则匹配失败，抛出异常
			raise ParseError('Must start with subject, object, or verb not %s' % start)

			 

		
		
