#-- coding: utf8 --
'''
下载沪深股市所有股票的历史日k线数据到数据库
'''

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import pymongo
import time

class StockBarData(object):
    '''日k线数据类型'''
    def __init__(self):
        super(StockBarData, self).__init__()
        
        self.code = ''
        self.datetime = None
        self.date = ''
        self.open = 0
        self.high = 0
        self.close = 0
        self.low = 0
        self.volume = 0
        self.price_change = 0
        self.p_change = 0
        self.ma5 = 0
        self.ma10 = 0
        self.ma20 = 0
        self.v_ma5 = 0
        self.v_ma10 = 0
        self.v_ma20 = 0
        self.turnover = 0

class HSStocksLocalEngine(object):
    '''功能引擎（从tushare下载所有股票列表、下载历史日k线数据，并且保存到本地数据库）'''
    def __init__(self, dbName):
        super(HSStocksLocalEngine, self).__init__()
        self.dbName = dbName
        self.dataCount = 0
        self.emptyDataCount = 0
        self.db = None

    def startWork(self):
        '''引擎启动'''

        startTime = time.time()
        #下载股票列表
        print u'正在下载股票列表..'
        stocksData = ts.get_stock_basics()
        print u'股票列表数据获取完成\n'

        #获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.db = client[self.dbName]
        print u'MongoDB 连接成功\n'

        #开始下载入库操作
        self.dataCount = 0
        self.emptyDataCount = 0

        for theCode, row in stocksData.iterrows():
            self.dataCount += 1
            print '=========%ld=========' % self.dataCount
            stockName = row['name']
            codeName = '%s（%s）' % (theCode, stockName)
            needUpdate = self.needUpdateChecking(theCode)
            if needUpdate:
                self.downloadToLocal(theCode, stockName)
            else:
                print unicode(codeName, 'utf-8')
                print u'已经是最新数据\n'

        endTime = time.time()
        print u'已完成全部%s只股票更新（用时%.f秒）' % (self.dataCount, (endTime - startTime))
        print u'其中%s只股票数据不存在' % self.emptyDataCount

    def needUpdateChecking(self, theCode):
        '''数据库查询股票更新的日期，并判断是否需要更新，避免重复下载数据'''
        date = datetime.now()
        hour = date.strftime('%H')
        #下午三点收盘前，能获取的日k线数据是前一天的收盘数据，数据库记录为前一天
        if int(hour) < 15:
            oneDay = timedelta(1)
            date = date - oneDay
        dateStr = date.strftime('%Y-%m-%d')

        historyCollection = self.db['UpdateHistory']
        cursor = historyCollection.find({})
        historyDict = {}
        for data in cursor:
            historyDict = data

        if len(historyDict):
            if theCode in historyDict:
                historyDateStr = historyDict[theCode]
                if historyDateStr == dateStr:
                    return False
                else:
                    return True
            else:
                return True
        else:
            return True

    def updateHistory(self, theCode):
        date = datetime.now()
        hour = date.strftime('%H')
        #下午三点收盘前，能获取的日k线数据是前一天的收盘数据，数据库记录为前一天
        if int(hour) < 15:
            oneDay = timedelta(1)
            date = date - oneDay
        dateStr = date.strftime('%Y-%m-%d')

        historyCollection = self.db['UpdateHistory']
        cursor = historyCollection.find({})
        historyDict = {}
        for data in cursor:
            historyDict = data

        historyDict[theCode] = dateStr
        historyCollection.update_many({}, {'$set':historyDict}, upsert = True)

    def downloadToLocal(self, stockCode, stockName):
        ''' 下载某只股票的历史数据，并保存到数据库 '''

        codeName = '%s（%s）' % (stockCode, stockName)
        print unicode(codeName, 'utf-8')
        print u'正在下载历史数据'
        data = ts.get_hist_data(stockCode, retry_count = 10, pause = 1)
        #上市前申购中的股票数据为None
        if data is None:
            print u'该股票数据不存在\n'
            self.emptyDataCount += 1
        else:
            data.sort_index(inplace = True)
            print u'历史数据下载完成'

            collection = self.db[theCode]
            collection.create_index('datetime')
            for date, row in data.iterrows():
                bar = StockBarData()
    
                bar.code = stockCode
                bar.date = '%s' % date
                bar.datetime = datetime.strptime(date, '%Y-%m-%d')
                bar.open = row['open']
                bar.high = row['high']
                bar.close = row['close']
                bar.low = row['low']
                bar.volume = row['volume']
                bar.price_change = row['price_change']
                bar.p_change = row['p_change']
                bar.ma5 = row['ma5']
                bar.ma10 = row['ma10']
                bar.ma20 = row['ma20']
                bar.v_ma5 = row['v_ma5']
                bar.v_ma10 = row['v_ma10']
                bar.v_ma20 = row['v_ma20']
                bar.turnover = row['turnover']
                #保存到数据库
                collection.update_many({'datetime':bar.datetime}, {'$set':bar.__dict__}, upsert = True)
            print u'数据更新完成\n'
        self.updateHistory(stockCode)

engine = HSStocksLocalEngine(dbName = 'Stocks_Daily_Db' )
engine.startWork()
