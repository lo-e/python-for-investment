#coding: utf8
import pdb

import thread

def action(a, b):
	print a, b

def action1(a, b):
	print a, b

def action2(a, b):
	print a, b

thread.start_new_thread(action, (1, 2,))
print 'yes'
thread.start_new_thread(action1, (5, 6,))
print 'ok'
print 'xyz'
thread.start_new_thread(action2, (8, 9,))
print 'abc'



