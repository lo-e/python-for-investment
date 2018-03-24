#-- coding: utf-8 --

import pymongo
from datetime import datetime, timedelta
from vnpy.trader.vtObject import VtTickData
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
from vnpy.trader.app.ctaStrategy.ctaTemplate import BarGenerator
from time import time
from sys import exit

class TicksBarEngine(object):
    def __init__(self, symbol, kLine):
        super(TicksBarEngine, self).__init__()
        self.symbol = symbol
        self.kLine = kLine
        self.newDayTick = None
        # 获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        # tick数据数据库
        tickDb = client[TICK_DB_NAME]
        self.tickCollection = tickDb[symbol]
        self.tickCollection.create_index('datetime')
        # bar数据数据库
        barDbName = 'VnTrader_%ldMin_Db' % kLine
        barDb = client[barDbName]
        self.barCollection =barDb[symbol]
        self.barCollection.create_index('datetime')
        # 历史记录数据库
        self.historyCollection = barDb['UpdateHistory']
        self.historyCollection.create_index('code')

    def startWork(self):
        self.bm = BarGenerator(self.onBar, self.kLine, self.onXminBar)
        currentDate = None
        newData =  False
        startTime = 0
        count = 0

        startDate = self.startDateFromHistory(self.symbol)
        if not startDate:
            tickCursor = self.tickCollection.find().sort('datetime')
        else:
            flt = {'datetime': {'$gte': startDate}}
            tickCursor = self.tickCollection.find(flt).sort('datetime')
        for d in tickCursor:
            tick = VtTickData()
            tick.__dict__ = d

            tickDateStr = tick.datetime.strftime('%Y%m%d')
            tickDate = datetime.strptime(tickDateStr, '%Y%m%d')
            if not currentDate or currentDate != tickDate:
                # 新的一天k线初始化
                self.newDayTick = tick
                self.bm.manualInit()
                self.newDayTick = None

                if newData:
                    # 保存导入记录
                    self.updateHistory(self.symbol, currentDate)

                    sub = time() - startTime
                    print u'用时：', sub, 's'
                    print u'数据量：', count, '\n'
                    count = 0

                currentDate = tickDate
                # 检查是否有数据库记录
                if not self.needUpdateChecking(self.symbol, currentDate):
                    # 当天的数据已经存在，无需重复导入
                    newData = False
                else:
                    print '*'*6, tick.datetime.date(), '*'*6
                    newData = True
                    startTime = time()
            if newData:
                self.bm.updateTick(tick)
                count += 1

        print u'所有数据导入完成'


    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        if self.newDayTick:
            bar.endDatetime = self.newDayTick.datetime
        self.bm.updateBar(bar)

    def onXminBar(self, bar):
        """收到X分钟K线"""
        # 保存xMinBar到数据库
        self.barCollection.update_many({'datetime': bar.datetime}, {'$set': bar.__dict__}, upsert=True)

    def startDateFromHistory(self, symbol):
        flt = {'code': symbol}
        cursor = self.historyCollection.find(flt)
        updateHistory = None
        for dic in cursor:
            updateHistory = dic
        if not updateHistory:
            return None
        elif 'dateList' in updateHistory:
            endDate = updateHistory['dateList'][-1]
            restartDate = endDate + timedelta(1)
            return restartDate
        else:
            return None

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
    symbol = raw_input(u'合约代码【rb00.TB】：')
    if not symbol:
        print '输入有误'
        exit(0)

    kLine = int(raw_input(u'k线类型 【1】：'))
    if not kLine:
        print '输入有误'
        exit(0)

    engine = TicksBarEngine(symbol, kLine)
    engine.startWork()