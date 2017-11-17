#-- coding: utf-8 --

import tushare as ts
import pymongo
import time
from datetime import datetime, timedelta
from vnpy.trader.vtObject import VtTickData
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
import futuquant as ft

class TicksLocalEngine(object):
    '''功能引擎（从起始日期开始下载某只股票所有tick数据）'''
    def __init__(self, code, exchange, startDate):
        super(TicksLocalEngine, self).__init__()
        self.code = code
        self.exchange = exchange
        self.vtCode = code + '.' + exchange
        self.startDate = startDate
        self.tradingDays = []

        #获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.collection = client[TICK_DB_NAME][self.vtCode]
        self.collection.create_index('datetime')
        self.historyCollection = client[TICK_DB_NAME]['UpdateHistory']
        print unicode('\n======即将更新 %s 的tick数据（开始日期：%s）======\n' % (code, self.startDate), 'utf-8')
        print u'MongoDB连接成功\n'

    def startWork(self):
        #获取交易日列表
        self.requestTradingDays()
        #开始的日期
        date = datetime.strptime(self.startDate, '%Y-%m-%d')
        delta = timedelta(1)

        stop = False
        while not stop:
            if self.needUpdateChecking(date):
                self.downloadToLocal(date)

            if date.date() < datetime.now().date():
                #逐天下载
                date = date + delta
            else:
                #更新到当天，结束下载
                stop = True
                print u'======已完成所有更新======'

    def needUpdateChecking(self, date):
        '''检查数据库该日期的tick数据是否存在'''
        #过滤非交易日

        if len(self.tradingDays):
            #根据futuAPI的查询结果
            dateStr = date.strftime('%Y-%m-%d')
            if dateStr not in self.tradingDays:
                return False
        elif date.weekday() == 5 or date.weekday() == 6:
            #周末休市
            return False

         #查询数据库
        flt = {'code':self.code}        
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

    def updateHistory(self, date):
        '''更新数据库记录该日期的tick数据保存成功'''

        #查询数据库
        flt = {'code':self.code}        
        cursor = self.historyCollection.find(flt)
        #拿到历史记录
        codeHistory = {'code':self.code}
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
        self.historyCollection.update_many({'code':self.code}, {'$set':codeHistory}, upsert = True)

    def requestTradingDays(self):
        '''futu API查询交易日列表'''
        #服务器ip
        api_svr_ip = '119.29.141.202'
        #服务器端口
        api_svr_port = 11111
        #股票市场
        market = 'SH'
        #实例化行情上下文对象
        quote_ctx = ft.OpenQuoteContext(host = api_svr_ip, port = api_svr_port)
        #获取交易日列表
        todayStr = datetime.now().strftime('%Y-%m-%d')
        ret, trading_days = quote_ctx.get_trading_days(market, self.startDate, todayStr)
        if len(trading_days):
            self.tradingDays = trading_days

    def downloadToLocal(self, date):
        ''' 下载某天的tick数据，并保存到数据库 '''
        time.sleep(0.5)
        print '======%s======' % date.date()
        #获取tick数据
        tickData = ts.get_tick_data(code, date.strftime('%Y-%m-%d'))
        if len(tickData) > 6:
            #排除数据有误或者当天没有数据的情况
            for index, row in tickData.iterrows():
                tick = VtTickData()
                tick.date = date.strftime('%Y-%m-%d')
                tick.time = row['time']
                tick.datetime = datetime.strptime(tick.date + ' ' + tick.time, '%Y-%m-%d %H:%M:%S')
    
                tick.symbol = code
                tick.exchange = exchange
                tick.vcSymbol = self.vtCode
                tick.lastPrice = row['price']
                tick.lastvolume = row['volume']
                tick.askPrice1 = row['price']
                tick.bidPrice1 = row['price']
                #保存tick数据到数据库
                self.collection.update_many({'datetime':tick.datetime}, {'$set':tick.__dict__}, upsert = True)
            self.updateHistory(date)
            print u'数据更新\n'
        else:
            print unicode(tickData.ix[0]['time'], 'utf-8')
            print '\n'



if __name__ == '__main__':
    #合约代码
    code = raw_input('code: ')
    if not len(code):
        code = '600380'
    #交易所
    exchange = raw_input('exchange: ')
    if not len(exchange):
        exchange = 'SSE'
    #起始时间
    startDate = raw_input('start date: ')
    if not len(startDate):
        startDate = '2017-01-01'

    engine = TicksLocalEngine(code, exchange, startDate)
    engine.startWork()

