# -- coding: utf8 --

from nose.tools import *
from module.collect import *

#测试用例
def test_directions():
	assert_equal(scan('north'), [('direction','north')])
	result = scan('north south east')
	assert_equal(result, [('direction', 'north'),
						  ('direction', 'south'),
						  ('direction', 'east')])
#测试用例，测试输入动词
def test_verbs():
	assert_equal(scan('go'), [('verb', 'go')])
	result = scan('go kill eat')
	assert_equal(result, [('verb', 'go'),
						  ('verb', 'kill'),
						  ('verb', 'eat')])
#测试用例，测试输入修饰词
def test_stops():
	assert_equal(scan('the'), [('stop', 'the')])
	result = scan('the in of')
	assert_equal(result, [('stop', 'the'),
						  ('stop', 'in'),
						  ('stop', 'of')])
#测试用例，测试输入名词
def test_nouns():
	assert_equal(scan('bear'), [('noun', 'bear')])
	result = scan('bear princess')
	assert_equal(result, [('noun', 'bear'),
						  ('noun', 'princess')])
#测试用例，测试输入数字
def test_numbers():
	assert_equal(scan('1234'), [('number', '1234')])
	result = scan('3 91234')
	assert_equal(result, [('number', '3'),
						  ('number', '91234')])
#测试用例，测试输入错误内容
def test_errors():
	assert_equal(scan('ASDFADFASDF'), [('error', 'ASDFADFASDF')])
	result = scan('bear IAS princess')
	assert_equal(result, [('noun', 'bear'),
						  ('error', 'IAS'),
						  ('noun', 'princess')])

def test_number():
	assert_equal(number('12'), True)
	



