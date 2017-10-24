# -- coding: utf8 --

from nose.tools import *
from exercise47.game import Room
from exercise47.module.module_a import action
import exercise47
from bin import module_b

def setup():
	print 'SETUP!'

def teardown():
	print 'TEAR DOWN!'

def test_basic():
	print 'I RAN!'

def test_room():
	gold = Room('GoldRoom',
				'''This room has gold in it you can grab.There's a
				door to the north.''')
	assert_equal(gold.name, 'GoldRoom')
	assert_equal(gold.paths, {})

def test_room_paths():
	center = Room('Center', 'Test room in the center.')
	north = Room('North', 'Test room in the north.')
	south = Room('South', 'Test room in the south')

	center.add_paths({'north':north, 'south':south})
	assert_equal(center.go('north'), north)
	assert_equal(center.go('south'), south)

def test_map():
	start = Room('Start', 'You can go west and down a hole.')
	west = Room('Trees', 'There are trees here, you can go east.')
	down = Room('Dungeon', "It's dark down here, you can go up.")

	start.add_paths({'west':west, 'down':down})
	west.add_paths({'east':start})
	down.add_paths({'up':start})

	assert_equal(start.go('west'), west)
	assert_equal(start.go('west').go('east'), start)
	assert_equal(start.go('down').go('up'), start)

def test_action():
	assert_equal(action(5), 6)

def test_version():
	assert_equal(exercise47.version, '0.1.0') 

def test_name():
	assert_equal(module_b.name, 'loe')