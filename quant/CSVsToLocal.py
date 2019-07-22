#-- coding: utf-8 --

import pymongo
import datetime
from vnpy.trader.object import TickData, BarData
from vnpy.app.cta_strategy.base import TICK_DB_NAME, DAILY_DB_NAME, MINUTE_DB_NAME, MinuteDataBaseName
import os
import csv
from time import time
from sys import exit
import re

#====== 交易时间 ======
#商品期货
MORNING_START_CF = datetime.time(9, 0)
MORNING_REST_CF = datetime.time(10, 15)
MORNING_RESTART_CF = datetime.time(10, 30)
MORNING_END_CF = datetime.time(11, 30)
AFTERNOON_START_CF = datetime.time(13, 30)
AFTERNOON_END_CF = datetime.time(15, 0)

# 商品期货夜盘时间
NIGHT_START_CF = datetime.time(21, 0)
NIGHT_END_CF_N = datetime.time(23, 0) # 到夜间收盘
NIGHT_END_CF_NM = datetime.time(1, 0) # 到凌晨收盘
NIGHT_END_CF_M = datetime.time(2, 30) # 到凌晨收盘

#股指期货
MORNING_START_SF = datetime.time(9, 30)
MORNING_END_SF = datetime.time(11, 30)
AFTERNOON_START_SF = datetime.time(13, 0)
AFTERNOON_END_SF = datetime.time(15, 0)


class CSVsTickLocalEngine(object):
    def __init__(self, type, night):
        super(CSVsTickLocalEngine, self).__init__()
        # 合约类型，不同品种期货交易时间特别是夜盘时间会有所差别，为了剔除无效数据而设置 1、商品期货  2、股指期货
        self.dataType = type
        # 夜盘时间类型
        self.night = night
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.tickDB = client[TICK_DB_NAME]
        self.historyCollection = self.tickDB['UpdateHistory']
        self.historyCollection.create_index('code')

    def startWork(self):
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                dirName = ''
                currentDate = None
                currentSymbol = ''
                count = 0

                # 确定合约【由文件夹名称决定，因为主力合约只能在文件夹名称中确定】
                if '\\' in root:
                    currentSymbol =  root.split('\\')[-1]
                    if not currentSymbol or (not currentSymbol.endswith('00')):
                        continue

                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                if 'tick' not in root:
                    continue

                # 确定日期
                if '.'in theFile:
                    pos = theFile.index('.')
                    dateStr = theFile[:pos]
                    currentDate = datetime.datetime.strptime(dateStr, '%Y%m%d')

                # 合约不存在
                if not currentSymbol:
                    print('*'*6)
                    print(u'没有找到合约')
                    print('*'*6)
                    exit(0)

                # 检查是否有数据库记录
                if currentDate and (not self.needUpdateChecking(currentSymbol, currentDate)):
                    continue

                if '.csv' in theFile:
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        # 开始导入数据
                        startTime = time()

                        for row in reader:
                            count += 1
                            if count == 1:
                                print('=' * 6, currentSymbol, ' ', currentDate.date(), '=' * 6)

                            # 过滤无效数据
                            timeStr = row['time']
                            theLen = len(timeStr)
                            if theLen < 9:
                                sub = 9 - theLen
                                timeStr = '0' * sub + timeStr

                            '''
                            hour = int(timeStr[0:2])
                            minute = int(timeStr[2:4])
                            second = int(timeStr[4:6])
                            microSecond = int(timeStr[6:9])
                            if hour < 0 or hour > 59 or minute < 0 or minute > 59 or second < 0 or second > 59 or microSecond < 0 or microSecond > 999:
                                print u'删除时间格式错误数据：%s' % timeStr
                                continue
                            '''

                            try:
                                tickTime = datetime.datetime.strptime(timeStr, '%H%M%S%f')
                            except Exception:
                                print(f'时间转换异常：{timeStr}')
                                raise
                                exit(0)

                            t = tickTime.time()
                            fakeData = True
                            if self.dataType == 1:
                                # 商品期货
                                if  self.night == 0:
                                    # 无夜盘交易
                                    if ((MORNING_START_CF <= t < MORNING_REST_CF)
                                        or (MORNING_RESTART_CF <= t < MORNING_END_CF)
                                        or (AFTERNOON_START_CF <= t < AFTERNOON_END_CF)):
                                        fakeData = False
                                elif self.night  ==  1:
                                    # 夜间23:00收盘
                                    if ((MORNING_START_CF <= t < MORNING_REST_CF)
                                        or (MORNING_RESTART_CF <= t < MORNING_END_CF)
                                        or (AFTERNOON_START_CF <= t < AFTERNOON_END_CF)
                                        or (NIGHT_START_CF <= t < NIGHT_END_CF_N)):
                                        fakeData = False
                                elif self.night == 2:
                                    # 凌晨1:00收盘
                                    if ((MORNING_START_CF <= t < MORNING_REST_CF)
                                        or (MORNING_RESTART_CF <= t < MORNING_END_CF)
                                        or (AFTERNOON_START_CF <= t < AFTERNOON_END_CF)
                                        or (NIGHT_START_CF <= t)
                                        or (NIGHT_END_CF_NM > t)):
                                        fakeData = False
                                elif self.night == 3:
                                    # 凌晨2:30收盘
                                    if ((MORNING_START_CF <= t < MORNING_REST_CF)
                                            or (MORNING_RESTART_CF <= t < MORNING_END_CF)
                                            or (AFTERNOON_START_CF <= t < AFTERNOON_END_CF)
                                            or (NIGHT_START_CF <= t)
                                            or (NIGHT_END_CF_M > t)):
                                        fakeData = False

                            elif self.dataType == 2:
                                # 股指期货
                                if ((MORNING_START_SF <= t < MORNING_END_SF) or (
                                                AFTERNOON_START_SF <= t < AFTERNOON_END_SF)):
                                    fakeData = False

                            theDate = row['calendarday']
                            theTime = tickTime.strftime('%H:%M:%S.%f')
                            theDatetime = datetime.datetime.strptime(theDate + ' ' + theTime, '%Y%m%d %H:%M:%S.%f')

                            # 数据库collection
                            collection = self.tickDB[currentSymbol]
                            collection.create_index('datetime')
                            if fakeData:
                                print(t)
                                print('【剔除无效数据】')
                                # 删除已保存的数据库数据
                                flt = {'datetime': theDatetime}
                                cursor = collection.find(flt)
                                if cursor.count():
                                    print('【剔除无效‘数据库’数据】')
                                collection.delete_many(flt)
                                continue

                            # 创建VtTickData对象
                            gateway_name = ''
                            symbol = row['instrument']
                            exchange = None

                            tick = TickData(gateway_name=gateway_name, symbol=symbol, exchange=exchange, datetime=theDatetime)
                            tick.last_price = float(row['lastp'])
                            tick.volume = int(float(row['volume']))
                            tick.open_interest = int(float(row['openinterest']))
                            tick.ask_price_1 = float(row['ask1'])
                            tick.ask_volume_1 = int(float(row['asksz1']))
                            tick.bid_price_1 = float(row['bid1'])
                            tick.bid_volume_1 = int(float(row['bidsz1']))
                            tick.date = theDate
                            tick.time = theTime
                            # 保存tick到数据库
                            collection.update_many({'datetime': tick.datetime}, {'$set': tick.__dict__}, upsert = True)

                        # 打印进程
                        if count:
                            sub = time() - startTime
                            print('用时：', sub, 's')
                            print('数据量：', count, '\n')
                        #  保存记录
                        if currentDate and count:
                            self.updateHistory(currentSymbol, currentDate)
        print('所有数据导入完成')

    def needUpdateChecking(self, symbol, date):
        '''检查数据库该日期的tick数据是否存在'''
        #查询数据库
        flt = {'code':symbol}
        cursor = self.historyCollection.find(flt)
        #拿到历史记录
        codeHistory = {}
        for dic in cursor:
            codeHistory = dic
        #历史日期记录
        dateList = []
        if 'dateList' in codeHistory:
            dateList = codeHistory['dateList']
        #记录新的日期
        if date in dateList:
            return False
        else:
            return True

    def updateHistory(self, symbol, date):
        '''更新数据库记录该日期的tick数据保存成功'''
        #查询数据库
        flt = {'code':symbol}
        cursor = self.historyCollection.find(flt)
        #拿到历史记录
        codeHistory = {'code':symbol}
        for dic in cursor:
            codeHistory = dic
        #历史日期记录
        dateList = []
        if 'dateList' in codeHistory:
            dateList = codeHistory['dateList']
        #记录新的日期
        if date not in dateList:
            dateList.append(date)

        codeHistory['dateList'] = dateList
        #更新数据库
        self.historyCollection.update_many({'code':symbol}, {'$set':codeHistory}, upsert = True)

class CSVs1TokenBarLocalEngine(object):
    def __init__(self, duration:str):
        super(CSVs1TokenBarLocalEngine, self).__init__()
        # 周期
        self.duration = duration
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        self.client = pymongo.MongoClient('localhost', 27017)

    def startWork(self):
        totalCount = 0
        totalStartTime = time()
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                count = 0
                startTime = time()

                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                if '\\' in root:
                    dirName = root.split('\\')[-1]

                if '.csv' in theFile and dirName == self.duration:
                    if dirName == '1d':
                        db_name = DAILY_DB_NAME
                    elif dirName == '1m' or dirName == '5m' or dirName == '15m' or dirName == '30m':
                        duration = re.sub("\D", "", dirName)
                        db_name = MinuteDataBaseName(duration)
                    else:
                        print('输入的周期不正确！！')
                        exit(0)
                    self.bar_db = self.client[db_name]
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        # 开始导入数据
                        for row in reader:
                            # 合约
                            symbol = row['symbol']
                            if not symbol:
                                print('合约不存在')
                                continue

                            # 确定日期
                            date = row['datetime']
                            if not date:
                                print('日期不存在')
                                continue
                            try:
                                theDatetime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                            except Exception:
                                print(f'日期转换异常：{date}')
                                raise
                                exit(0)

                            count += 1
                            totalCount += 1
                            if count == 1:
                                print('=' * 6, symbol, '=' * 6)

                            # 数据库collection
                            collection = self.bar_db[symbol]
                            collection.create_index('datetime')
                            # 创建BarData对象
                            bar = BarData(gateway_name='', symbol=symbol, exchange=None, datetime=theDatetime, endDatetime=None)
                            bar.open_price = float(row['open'])
                            bar.close_price = float(row['close'])
                            bar.high_price = float(row['high'])
                            bar.low_price = float(row['low'])
                            bar.volume = float(row['volume'])
                            # 保存bar到数据库
                            collection.update_many({'datetime': bar.datetime}, {'$set': bar.__dict__}, upsert = True)
                # 打印进程
                if count:
                    sub = time() - startTime
                    print('用时：', sub, 's')
                    print('数据量：', count, '\n')

        # 打印进程
        print('所有数据导入完成')
        if totalCount:
            sub = time() - totalStartTime
            print('总用时：', sub, 's')
            print(u'总数据量：', totalCount, '\n')

class CSVsCryptocompareBarLocalEngine(object):
    def __init__(self, duration:str):
        super(CSVsCryptocompareBarLocalEngine, self).__init__()
        # 周期
        self.duration = duration
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        self.client = pymongo.MongoClient('localhost', 27017)

    def startWork(self):
        totalCount = 0
        totalStartTime = time()
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                count = 0
                startTime = time()

                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                # 排除非Cryptocompare数据
                if not 'cryptocompare' in root:
                    continue

                if '\\' in root:
                    dirName = root.split('\\')[-1]

                if '.csv' in theFile and dirName == self.duration:
                    if dirName == '1d':
                        db_name = DAILY_DB_NAME
                    elif dirName == '1m' or dirName == '5m' or dirName == '15m' or dirName == '30m':
                        duration = re.sub("\D", "", dirName)
                        db_name = MinuteDataBaseName(duration)
                    else:
                        print('输入的周期不正确！！')
                        exit(0)
                    self.bar_db = self.client[db_name]
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        # 开始导入数据
                        for row in reader:
                            # 合约
                            symbol = row['symbol']
                            if not symbol:
                                print('合约不存在')
                                continue

                            # 确定日期
                            date = row['datetime']
                            if not date:
                                print('日期不存在')
                                continue
                            try:
                                theDatetime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                            except Exception:
                                print(f'日期转换异常：{date}')
                                raise
                                exit(0)

                            count += 1
                            totalCount += 1
                            if count == 1:
                                print('=' * 6, symbol, '=' * 6)

                            # 数据库collection
                            collection = self.bar_db[symbol]
                            collection.create_index('datetime')
                            # 创建BarData对象
                            bar = BarData(gateway_name='', symbol=symbol, exchange=None, datetime=theDatetime, endDatetime=None)
                            bar.open_price = float(row['open'])
                            bar.close_price = float(row['close'])
                            bar.high_price = float(row['high'])
                            bar.low_price = float(row['low'])
                            bar.volume = float(row['volumeto'])
                            # 保存bar到数据库
                            collection.update_many({'datetime': bar.datetime}, {'$set': bar.__dict__}, upsert = True)
                # 打印进程
                if count:
                    sub = time() - startTime
                    print('用时：', sub, 's')
                    print('数据量：', count, '\n')

        # 打印进程
        print('所有数据导入完成')
        if totalCount:
            sub = time() - totalStartTime
            print('总用时：', sub, 's')
            print(u'总数据量：', totalCount, '\n')

if __name__ == '__main__':
    # Tick
    """
    type = int(input(u'合约类型【1、商品 2、股指】：'))
    if type != 1 and type != 2 :
        print('输入有误')
        exit(0)

    night = 0
    if type == 1:
        night = int(input(u'夜盘时间类型【0、无 1、夜间23:00 2、凌晨1:00 3、凌晨2:30】：'))
        if night != 0 and night != 1 and night != 2 and night != 3:
            print('输入有误')
            exit(0)
    engine = CSVsTickLocalEngine(type, night)
    engine.startWork()
    """

    """
    # 1Token_Bar
    engine = CSVs1TokenBarLocalEngine(duration='1d')
    engine.startWork()
    """

    # Cryptocompare_Bar
    engine = CSVsCryptocompareBarLocalEngine(duration='1d')
    engine.startWork()
