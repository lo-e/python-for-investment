#-- coding: utf-8 --

from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
from vnpy.trader.object import BarData
from vnpy.app.cta_strategy.base import DAILY_DB_NAME, MinuteDataBaseName, HourDataBaseName

class BarLocalEngine(object):
    def __init__(self, duration:str):
        super(BarLocalEngine, self).__init__()
        self.client = MongoClient('localhost', 27017, serverSelectionTimeoutMS = 600)

    def Crypto_1Min_Daily(self, symbol, start_date='', end_date=''):
        Daily_db = self.client[DAILY_DB_NAME]
        Daily_collection = Daily_db[symbol]
        Min_db = self.client[MinuteDataBaseName(duration=1)]
        Min_collection = Min_db[symbol]
        flt = {}
        start_end = {}
        if start_date:
            start_end['$gte'] = datetime.strptime(start_date, '%Y-%m-%d')
        if start_date:
            start_end['$lte'] = datetime.strptime(end_date, '%Y-%m-%d')
        if start_end:
            flt = {'datetime': start_end}
        cursor = Min_collection.find(flt).sort('datetime', ASCENDING)
        next_datetime = None
        daily_bar = None
        daily_bar_datetime = None
        daily_bar_end = None
        for dic in cursor:
            the_datetime = dic['datetime']
            """ fake """
            if the_datetime >= datetime.strptime('2019-09-03 07:56:00', '%Y-%m-%d %H:%M:%S'):
                a = 2
            if not next_datetime:
                next_datetime = datetime.strptime(f'{the_datetime.year}-{the_datetime.month}-{the_datetime.day} 08:00:00',
                                                  '%Y-%m-%d %H:%M:%S')
                if the_datetime > next_datetime:
                    next_datetime += timedelta(days=1)
                daily_bar_datetime = next_datetime
                temp = daily_bar_datetime + timedelta(days=1)
                daily_bar_end = datetime.strptime(f'{temp.year}-{temp.month}-{temp.day} 07:59:00',
                                                  '%Y-%m-%d %H:%M:%S')
            if the_datetime == next_datetime:
                if the_datetime == daily_bar_datetime:
                    # Daily的开始
                    daily_bar = BarData(gateway_name='', symbol=dic['symbol'], exchange=None, datetime=daily_bar_datetime, endDatetime=None)
                    daily_bar.open_price = dic['open_price']
                    daily_bar.close_price = dic['close_price']
                    daily_bar.high_price = dic['high_price']
                    daily_bar.low_price = dic['low_price']
                else:
                    if not daily_bar:
                        raise('出现异常，检查代码！')

                    daily_bar.close_price = dic['close_price']
                    daily_bar.high_price = max(daily_bar.high_price, dic['high_price'])
                    daily_bar.low_price = min(daily_bar.low_price, dic['low_price'])

                next_datetime += timedelta(minutes=1)
                if the_datetime == daily_bar_end:
                    # Daily的结束
                    # 保存bar到数据库
                    print(f'保存Daily数据：{symbol}\t{daily_bar_datetime}')
                    Daily_collection.update_many({'datetime': daily_bar.datetime}, {'$set': daily_bar.__dict__}, upsert=True)

                    daily_bar_datetime = next_datetime
                    temp = daily_bar_datetime + timedelta(days=1)
                    daily_bar_end = datetime.strptime(f'{temp.year}-{temp.month}-{temp.day} 07:59:00',
                                                      '%Y-%m-%d %H:%M:%S')

            elif the_datetime > next_datetime:
                lost_minutes = []
                while next_datetime < the_datetime:
                    lost_minutes.append(datetime.strftime(next_datetime, '%Y-%m-%d %H:%M:%S'))
                    next_datetime += timedelta(minutes=1)
                print(f'数据缺失：\n{lost_minutes}')

                next_datetime = the_datetime + timedelta(minutes=1)
                if the_datetime <= daily_bar_end:
                    if not daily_bar:
                        # Daily的开始
                        daily_bar = BarData(gateway_name='', symbol=dic['symbol'], exchange=None, datetime=daily_bar_datetime,
                                            endDatetime=None)
                        daily_bar.open_price = dic['open_price']
                        daily_bar.close_price = dic['close_price']
                        daily_bar.high_price = dic['high_price']
                        daily_bar.low_price = dic['low_price']
                    else:
                        daily_bar.close_price = dic['close_price']
                        daily_bar.high_price = max(daily_bar.high_price, dic['high_price'])
                        daily_bar.low_price = min(daily_bar.low_price, dic['low_price'])

                    if the_datetime == daily_bar_end:
                        # Daily的结束
                        # 保存bar到数据库
                        print(f'保存数据库：{symbol}\t{daily_bar_datetime}')
                        Daily_collection.update_many({'datetime': daily_bar.datetime}, {'$set': daily_bar.__dict__},
                                                     upsert=True)

                        daily_bar_datetime = next_datetime
                        temp = daily_bar_datetime + timedelta(days=1)
                        daily_bar_end = datetime.strptime(f'{temp.year}-{temp.month}-{temp.day} 07:59:00',
                                                          '%Y-%m-%d %H:%M:%S')

                else:
                    if daily_bar:
                        # Daily的结束
                        # 保存bar到数据库
                        print(f'保存数据库：{symbol}\t{daily_bar_datetime}')
                        Daily_collection.update_many({'datetime': daily_bar.datetime}, {'$set': daily_bar.__dict__},
                                                     upsert=True)

                    daily_bar_datetime = datetime.strptime(
                        f'{the_datetime.year}-{the_datetime.month}-{the_datetime.day} 08:00:00',
                        '%Y-%m-%d %H:%M:%S')
                    temp = daily_bar_datetime + timedelta(days=1)
                    daily_bar_end = datetime.strptime(f'{temp.year}-{temp.month}-{temp.day} 07:59:00',
                                                      '%Y-%m-%d %H:%M:%S')

                    # Daily的开始
                    daily_bar = BarData(gateway_name='', symbol=dic['symbol'], exchange=None,
                                        datetime=daily_bar_datetime,
                                        endDatetime=None)
                    daily_bar.open_price = dic['open_price']
                    daily_bar.close_price = dic['close_price']
                    daily_bar.high_price = dic['high_price']
                    daily_bar.low_price = dic['low_price']

            else:
                if not daily_bar:
                    continue
                else:
                    raise ('出现异常，检查代码！')

if __name__ == '__main__':
    #"""
    # 1Token_Bar
    engine = BarLocalEngine(duration='1m')
    symbol = 'ETH.USD.Q.OKEF'
    start_date = '2019-9-01'
    end_date = '2019-10-01'
    engine.Crypto_1Min_Daily(symbol=symbol, start_date=start_date, end_date=end_date)
    #"""