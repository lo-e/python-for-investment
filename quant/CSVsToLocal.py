#-- coding: utf-8 --

import pymongo
import datetime
from vnpy.trader.vtObject import VtTickData
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
import os
import csv
from time import time
from sys import exit

#====== 交易时间 ======
#商品期货
MORNING_START_CF = datetime.time(9, 0)
MORNING_REST_CF = datetime.time(10, 15)
MORNING_RESTART_CF = datetime.time(10, 30)
MORNING_END_CF = datetime.time(11, 30)
AFTERNOON_START_CF = datetime.time(13, 30)
AFTERNOON_END_CF = datetime.time(15, 0)
NIGHT_START_CF = datetime.time(21, 0)
NIGHT_END_CF = datetime.time(23, 0)

#股指期货
MORNING_START_SF = datetime.time(9, 30)
MORNING_END_SF = datetime.time(11, 30)
AFTERNOON_START_SF = datetime.time(13, 0)
AFTERNOON_END_SF = datetime.time(15, 0)

class csvsLocalEngine(object):
    def __init__(self, type):
        super(csvsLocalEngine, self).__init__()
        # 数据类型，不同品种期货交易时间特别是夜盘时间会有所差别，为了剔除无效数据而设置 1、商品期货  2、股指期货
        self.dataType = type
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.db = client[TICK_DB_NAME]
        self.historyCollection = self.db['UpdateHistory']
        self.historyCollection.create_index('code')

    def startWork(self):
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                currentDate = None
                currentSymbol = ''
                count = 0

                # 确定合约【由文件夹名称决定，因为主力合约只能在文件夹名称中确定】
                if '\\' in root:
                    currentSymbol =  root.split('\\')[-1]
                    currentSymbol = currentSymbol  + '.TB'

                # 确定日期
                if '.'in theFile:
                    pos = theFile.index('.')
                    dateStr = theFile[:pos]
                    currentDate = datetime.datetime.strptime(dateStr, '%Y%m%d')

                # 合约不存在
                if not currentSymbol:
                    print '*'*6
                    print u'没有找到合约'
                    print  '*'*6
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
                                print '=' * 6, currentSymbol, ' ', currentDate.date(), '=' * 6

                            # 过滤无效数据
                            tickTime = datetime.datetime.strptime(row['time'], '%H%M%S%f')
                            t = tickTime.time()
                            fakeData = True
                            if self.dataType == 1:
                                # 商品期货
                                if ((MORNING_START_CF <= t < MORNING_REST_CF) or (
                                                MORNING_RESTART_CF <= t < MORNING_END_CF) or (
                                                AFTERNOON_START_CF <= t < AFTERNOON_END_CF) or (
                                                NIGHT_START_CF <= t < NIGHT_END_CF)):
                                    fakeData = False
                            elif self.dataType == 2:
                                # 股指期货
                                if ((MORNING_START_SF <= t < MORNING_END_SF) or (
                                                AFTERNOON_START_SF <= t < AFTERNOON_END_SF)):
                                    fakeData = False

                            if fakeData:
                                print t
                                print u'【剔除无效数据】'
                                continue

                            # 创建VtTickData对象
                            tick = VtTickData()
                            tick.vtSymbol = row['instrument']
                            tick.lastPrice = float(row['lastp'])
                            tick.volume = int(row['volume'])
                            tick.openInterest = int(row['openinterest'])
                            tick.askPrice1 = float(row['ask1'])
                            tick.askVolume1 = int(row['asksz1'])
                            tick.bidPrice1 = float(row['bid1'])
                            tick.bidVolume1 = int(row['bidsz1'])
                            tick.date = row['calendarday']
                            tick.time = tickTime.strftime('%H:%M:%S.%f')
                            tick.datetime = datetime.datetime.strptime(tick.date + ' ' + tick.time, '%Y%m%d %H:%M:%S.%f')

                            # 数据库collection
                            collection = self.db[currentSymbol]
                            collection.create_index('datetime')
                            # 保存tick到数据库
                            collection.update_one({'datetime': tick.datetime}, {'$set': tick.__dict__}, upsert = True)
                        # 打印进程
                        if count:
                            sub = time() - startTime
                            print u'用时：', sub, 's'
                            print u'数据量：', count, '\n'
                        #  保存记录
                        if currentDate and count:
                            self.updateHistory(currentSymbol, currentDate)
        print u'所有数据导入完成'

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


if __name__ == '__main__':
    type = raw_input(u'数据类型【1、商品 2、股指】：')
    engine = csvsLocalEngine(int(type))
    engine.startWork()
