# -- coding: utf-8 --

from pymongo import MongoClient, ASCENDING, DESCENDING
from vnpy.app.cta_strategy.base import TICK_DB_NAME, MINUTE_DB_NAME, DAILY_DB_NAME, MinuteDataBaseName, HourDataBaseName
from datetime import datetime
from vnpy.trader.object import TickData

def test_tick():
    client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=600)  # Mongo连接
    client.server_info()
    dbTick = client[TICK_DB_NAME]
    symbol_list = ['BTCUSD', 'ETHUSD']
    for symbol in symbol_list:
        cl = dbTick[symbol]
        cl.create_index('datetime')  # 添加索引
        start = datetime.strptime('2019-11-18 07:59:50', '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime('2019-11-19 08:00:10', '%Y-%m-%d %H:%M:%S')
        flt = {'datetime': {'$gte': start,
                            '$lte': end}}
        cursor = cl.find({}).sort('datetime', DESCENDING)
        count = 0
        for dic in cursor:
            tick = TickData(gateway_name='', symbol='', exchange=None, datetime=None)
            tick.__dict__ = dic
            print(f'vt_symbol:{tick.vt_symbol}\t{tick.datetime}\t{tick.symbol}\t{tick.last_price}')
            count += 1
            if count >= 6:
                print('\n')
                break

def test_minute():
    client = MongoClient('localhost', 27017)
    db = client[MINUTE_DB_NAME]
    symbol_list = ['BTCUSD.BYBIT', 'ETHUSD.BYBIT']
    for symbol in symbol_list:
        collection = db[symbol]
        start = datetime.strptime('2020-3-24 00:00:00', '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime('2020-3-25 00:00:00', '%Y-%m-%d %H:%M:%S')
        flt = {'datetime': {'$gte': start,
                            '$lte': end}}
        cursor = collection.find().sort('datetime', DESCENDING)
        count = 0
        for dic in cursor:
            print(dic['vt_symbol'], dic['datetime'], dic['open_price'])
            count += 1
            if count >= 6:
                print('\n')
                break

def test_daily():
    client = MongoClient('localhost', 27017)
    db = client[DAILY_DB_NAME]
    symbol_list = ['BTCUSD.BYBIT', 'ETHUSD.BYBIT']
    for symbol in symbol_list:
        collection = db[symbol]
        start = datetime.strptime('2019-11-27 00:00:00', '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime('2019-11-27 00:06:00', '%Y-%m-%d %H:%M:%S')
        flt = {'datetime': {'$gte': start,
                            '$lte': end}}
        cursor = collection.find({}).sort('datetime', DESCENDING)
        count = 0
        for dic in cursor:
            symbol = dic['symbol']
            the_datetime = dic['datetime']
            open_price = dic['open_price']
            high_price = dic['high_price']
            low_price = dic['low_price']
            close_price = dic['close_price']
            print(f'{symbol}\t{the_datetime}\t{open_price}\t{high_price}\t{low_price}\t{close_price}')
            count += 1
            if count >= 6:
                print('\n')
                break

if __name__ == '__main__':
    #test_tick()
    #test_minute()
    test_daily()





