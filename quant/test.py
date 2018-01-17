# -- coding: utf-8 --

import pandas as pd
import tushare as ts

def nothing():
    print 'no'

def action():
    print 'yes'
    nothing()

if __name__ == '__main__':
    action()