# -- coding: utf8 --

from nose.tools import *
from module.parsor import *

parse = Parse()
#测试用例
def test_peek():
	word_list = scan('bear go up')
	assert_equal(parse.peek(word_list), 'noun')

#测试用例
def test_match():
	word_list = scan('bear go up')
	assert_equal(parse.match(word_list, 'noun'), ('noun', 'bear'))

#测试用例
def test_skip():
	word_list = scan('bear go up')
	parse.skip(word_list, 'noun')
	assert_equal(word_list, [('verb', 'go'), ('direction', 'up')])

#测试用例
def test_parse_verb():
	word_list = scan('bear go up')
	parse.match(word_list, 'direction')
	assert_raises(parse.parse_verb(word_list))

#测试用例
def test_parse_object():
	word_list = scan('bear go up')
	assert_raises(parse.parse_object(word_list))
	parse.match(word_list, 'noun')
	assert_raises(parse.parse_object(word_list))

#测试用例
def test_parse_subject():
	word_list = scan('go the in of up')
	sentence = parse.parse_subject(word_list, ('abc', 'xyz'))
	assert_equal(sentence.subject, 'xyz')

#测试用例
def test_sentense():
	word_list = scan('go the in of up')
	sentence = parse.parse_sentence(word_list)
	assert_equal(sentence.subject, 'player')

	word_list = scan('bear go the in of up')
	sentence = parse.parse_sentence(word_list)
	assert_equal(sentence.subject, 'bear')
