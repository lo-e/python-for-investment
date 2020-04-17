# -- coding: utf-8 --

from datetime import datetime
from vnpy.trader.object import BarData
from vnpy.trader.object import TradeData
from vnpy.trader.constant import Exchange

if __name__ == '__main__':
    #a = BarData(gateway_name='', symbol='', exchange=None, datetime=None, endDatetime=None)
    a = TradeData(gateway_name='abc', symbol='abc', exchange=Exchange.RQ, orderid='abc', tradeid='abc')
    b = a.__dict__
    c = f'{b}'
    print(type(b))
    print(type(c))
    print(c)





