#-- coding: utf-8 --

import pymongo
import datetime
from vnpy.trader.vtObject import VtBarData
from vnpy.trader.app.ctaStrategy.ctaBase import DAILY_DB_NAME
import os
import csv
from time import time
from sys import exit
from vnpy.trader.app.ctaStrategy.stgEarningManager import stgEarningManager
from collections import OrderedDict

class csvsLocalEngine(object):
    def __init__(self):
        super(csvsLocalEngine, self).__init__()
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.db = client[DAILY_DB_NAME]

    def startWork(self):
        totalCount = 0
        totalStartTime = time()
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                currentSymbol = ''
                count = 0

                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                if '\\' in root:
                    dirName = root.split('\\')[-1]

                if '.csv' in theFile and dirName == 'md':
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        # 开始导入数据
                        for row in reader:
                            # 合约
                            if row['symbol']:
                                currentSymbol = row['symbol']
                                startTime = time()
                                # 打印进程
                                if count:
                                    sub = time() - startTime
                                    print u'用时：', sub, 's'
                                    print u'数据量：', count, '\n'
                                count = 0
                            if not currentSymbol:
                                print u'合约不存在'
                                continue

                            # 确定日期
                            date = row['date']
                            if not date:
                                print u'日期不存在'
                                continue
                            try:
                                theDate = datetime.datetime.strptime(date, '%Y%m%d')
                            except Exception:
                                print u'日期转换异常：%s' % date
                                raise
                                exit(0)

                            count += 1
                            totalCount += 1
                            if count == 1:
                                print '=' * 6, currentSymbol, '=' * 6

                            # 数据库collection
                            collection = self.db[currentSymbol + '.TB']
                            collection.create_index('datetime')
                            # 创建VtBarData对象
                            bar = VtBarData()
                            bar.vtSymbol = currentSymbol
                            bar.datetime = theDate
                            bar.open = row['open']
                            bar.close = row['close']
                            bar.high = row['high']
                            bar.low = row['low']
                            bar.date = date
                            bar.volume = row['volume']
                            bar.openInterest = row['openInterest']
                            # 保存bar到数据库
                            collection.update_many({'datetime': bar.datetime}, {'$set': bar.__dict__}, upsert = True)
                # 打印进程
                if count:
                    sub = time() - startTime
                    print u'用时：', sub, 's'
                    print u'数据量：', count, '\n'

        # 打印进程
        print u'所有数据导入完成'
        if totalCount:
            sub = time() - totalStartTime
            print u'总用时：', sub, 's'
            print u'总数据量：', totalCount, '\n'

class lhbLoadingEngine(object):
    def __init__(self):
        super(lhbLoadingEngine, self).__init__()
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.db = client[DAILY_DB_NAME]

    # 导入交易所龙虎榜数据
    def lhbLoading(self):
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                if '\\' in root:
                    dirName = root.split('\\')[-1]

                if '.csv' in theFile and dirName == 'exchange':
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        # 开始导入数据
                        startTime = time()
                        for row in reader:
                            # 合约
                            instrument = row['instrument']
                            if not instrument:
                                continue

                            # 日期
                            dateStr = row['tradingday']
                            currentDate = datetime.datetime.strptime(dateStr, '%Y%m%d')
                            # 多头增减
                            buyInterestChange = float(row['buyInterestChange'])
                            buyInterestChange = round(buyInterestChange, 2)
                            # 空头增减
                            sellInterestChange = float(row['sellInterestChange'])
                            sellInterestChange = round(sellInterestChange, 2)
                            # 月份合约数据库
                            collection = self.db[instrument + '.TB']
                            collection.create_index('datetime')
                            # 查询数据库
                            flt = {'datetime': currentDate}
                            cursor = collection.find(flt)
                            # 拿到历史记录
                            barData = {}
                            for dic in cursor:
                                barData = dic
                            barData['buyInterestChange'] = buyInterestChange
                            barData['sellInterestChange'] = sellInterestChange
                            collection.update_many({'datetime': currentDate}, {'$set': barData}, upsert=True)

        print u'所有数据导入完成'

    # 导入淘宝龙虎榜数据
    def tblhbLoading(self):
        startTime = time()
        count = 0
        lastSymbol = ''
        currentSymbol = ''
        currentDate = None
        interestChange = 0
        dirName = ''

        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                if currentSymbol:
                    # 保存数据库
                    self.saveInterestChangeLocal(currentSymbol, currentDate, interestChange, dirName)
                    lastSymbol = ''
                    currentSymbol = ''
                    currentDate = None
                    interestChange = 0
                    dirName = ''

                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                if '\\' in root:
                    dirName = root.split('\\')[-1]

                if '.csv' in theFile and 'tb' in root:
                    print '--', theFile, '--'
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        # 开始导入数据
                        for row in reader:
                            # 合约
                            lastSymbol = currentSymbol
                            currentSymbol = row['期货合约代码']
                            if lastSymbol and lastSymbol != currentSymbol:
                                # 单一合约排名统计完成，保存数据库
                                self.saveInterestChangeLocal(lastSymbol, currentDate, interestChange, dirName)
                                # 统计清零
                                interestChange = 0

                            # 日期
                            dateStr = row['交易日期']
                            currentDate = datetime.datetime.strptime(dateStr, '%Y-%m-%d')

                            if dirName == 'buy':
                                # 多头增减
                                theChange = float(row['多头增减'])
                                theChange = round(theChange, 2)
                                interestChange += theChange
                            elif dirName == 'sell':
                                # 空头增减
                                theChange = float(row['空头增减'])
                                theChange = round(theChange, 2)
                                interestChange += theChange
                            else:
                                continue

                            count += 1

        if currentSymbol:
            # 保存数据库
            self.saveInterestChangeLocal(currentSymbol, currentDate, interestChange, dirName)

        print u'所有数据导入完成'
        print u'数据量：', count
        sub = time() - startTime
        print u'用时：', sub, 's'

    def saveInterestChangeLocal(self, symbol, date, interestChange, dirName):
        # 月份合约数据库
        collection = self.db[symbol + '.TB']
        # 查询数据库
        flt = {'datetime': date}
        cursor = collection.find(flt)
        # 拿到历史记录
        barData = {}
        for dic in cursor:
            barData = dic

        if barData:
            if dirName == 'buy':
                barData['buyInterestChange'] = interestChange
            elif dirName == 'sell':
                barData['sellInterestChange'] = interestChange

            collection.update_many({'datetime': date}, {'$set': barData}, upsert=True)

class csvsMainEngine(object):
    def __init__(self):
        super(csvsMainEngine, self).__init__()
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.db = client[DAILY_DB_NAME]

    def createIndex(self):
        dateStr = ''
        instrument = ''
        dirName = ''
        earningManager = stgEarningManager()
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                if '\\' in root:
                    dirName = root.split('\\')[-1]

                if not dirName or not dirName.endswith('00'):
                    continue

                if '.csv' in theFile:
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            # 日期
                            dateStr = row['tradingday']
                            # 月份合约
                            instrument = row['instrument']

                            if dateStr and instrument and dirName:
                                # 保存记录到文件
                                fileName = 'index_'
                                content = OrderedDict()
                                content['instrument'] = instrument
                                content['tradingday'] = dateStr
                                content['main'] = dirName
                                earningManager.updateDailyEarning(fileName, content)

                                print dirName, dateStr, instrument
                                instrument = ''
                                dateStr = ''
                                dirName = ''
                                break


    def processIndex(self):
        totalStartTime = time()
        count = 0
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                # 排除不合法文件
                if theFile.startswith('.'):
                    continue

                if '\\' in root:
                    dirName = root.split('\\')[-1]

                if '.csv' in theFile and dirName == 'main':
                    # 读取文件
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            # 日期
                            dateStr = row['tradingday']
                            currentDate = datetime.datetime.strptime(dateStr, '%Y%m%d')
                            # 主力合约
                            mainSymbol = row['main']
                            mainCollection = self.db[mainSymbol + '.TB']
                            #mainCollection.create_index('datetime')
                            # 查询数据库
                            flt = {'datetime': currentDate}
                            cursor = mainCollection.find(flt)
                            # 拿到历史记录
                            mainData = {}
                            for dic in cursor:
                                mainData = dic

                            # 月份合约
                            instrument = row['instrument']
                            # 月份合约数据库
                            subCollection = self.db[instrument + '.TB']
                            #subCollection.create_index('datetime')
                            # 查询数据库
                            flt = {'datetime': currentDate}
                            cursor = subCollection.find(flt)
                            # 拿到历史记录
                            barData = {}
                            for dic in cursor:
                                barData = dic
                            # 主力合约数据库
                            if barData:
                                if mainData:
                                    barData['_id'] = mainData['_id']
                                mainCollection.update_many({'datetime': currentDate}, {'$set': barData}, upsert=True)
                            count += 1

        print u'所有品种主力整理完成'
        print u'数据量：', count
        sub = time() - totalStartTime
        print u'用时：', sub, 's'

if __name__ == '__main__':
    '''
    # 每日数据导入数据库
    engine = csvsLocalEngine()
    engine.startWork()
    '''

    #'''
    # 龙虎榜数据导入
    engine = lhbLoadingEngine()
    engine.tblhbLoading()
    #'''

    '''
    # 生成主力文件
    engine = csvsMainEngine()
    engine.createIndex()
    '''

    '''
    # 主力合约整理
    engine = csvsMainEngine()
    engine.processIndex()
    '''
