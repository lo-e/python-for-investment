#-- coding: utf-8 --

import tushare as ts
import pymongo  
import time
from datetime import timedelta
import datetime
from vnpy.trader.vtObject import VtTickData
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
import futuquant as ft
import sys
import pandas as pd

#交易时间
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

class TicksLocalEngine(object):
    '''功能引擎（从起始日期开始下载某只股票所有tick数据）'''
    def __init__(self, code, exchange, asset, startDate):
        super(TicksLocalEngine, self).__init__()
        self.code = code
        self.exchange = exchange
        self.vtCode = code + '.' + exchange
        self.asset = asset
        self.startDate = startDate
        self.tradingDays = []
        self.cons = ts.get_apis()

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
        date = datetime.datetime.strptime(self.startDate, '%Y-%m-%d')
        delta = timedelta(1)

        stop = False
        endDate = (datetime.datetime.now()-delta).date()
        while not stop:
            if self.needUpdateChecking(date):
                self.downloadToLocal(date)

            if date.date() < endDate:
                #逐天下载
                date = date + delta
            else:
                #更新到当天，结束下载
                stop = True
                print u'======已完成所有更新======'
                self.end()

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
        todayStr = datetime.datetime.now().strftime('%Y-%m-%d')
        ret, trading_days = quote_ctx.get_trading_days(market, self.startDate, todayStr)
        if len(trading_days):
            self.tradingDays = trading_days
        quote_ctx.close()

    def downloadToLocal(self, date):
        ''' 下载某天的tick数据，并保存到数据库 '''
        time.sleep(0.5)
        print '======%s======' % date.date()
        #获取tick数据
        #tickData = ts.get_tick_data(code, date.strftime('%Y-%m-%d'))
        tickData = None
        if (self.asset == 1) or (self.asset == 2):
            #商品期货、股指期货
            tickData = ts.tick(self.code, self.cons, date.strftime('%Y-%m-%d'), asset = 'X')
        else:
            tickData = ts.tick(self.code, self.cons, date.strftime('%Y-%m-%d'))

        isDf = isinstance(tickData, pd.DataFrame)
        if isDf:
            #排除数据有误或者当天没有数据的情况
            lastDt = None
            mSecond = 0
            for index, row in tickData.iterrows():
                the = row['date']
                dt = the.to_datetime()
                t = dt.time()
                #过滤无效数据
                fakeData = True
                if self.asset == 1:
                    #商品期货
                    if ( (MORNING_START_CF <= t <MORNING_REST_CF) or (MORNING_RESTART_CF <= t < MORNING_END_CF) or (AFTERNOON_START_CF <= t < AFTERNOON_END_CF) or (NIGHT_START_CF <= t < NIGHT_END_CF)):
                        fakeData = False
                elif self.asset == 2:
                    #股指期货
                    if ( (MORNING_START_SF <= t < MORNING_END_SF) or (AFTERNOON_START_SF <= t < AFTERNOON_END_SF)):
                        fakeData = False

                if fakeData:
                    print dt
                    print u'【剔除无效数据】'
                    continue

                #自动修正夜盘的时间
                if (self.asset == 1) and (NIGHT_START_CF <= t < NIGHT_END_CF):
                    #商品期货夜盘
                    dt = dt - timedelta(1)

                #添加毫秒（tushare下载的tick数据没有毫秒导致相同秒的数据导入数据库会被覆盖缺失）
                if (not lastDt) or lastDt != dt:
                    mSecond = 0
                    lastDt = dt
                else:
                    mSecond += 100000
                dt = dt.replace(microsecond = mSecond)

                #数据封装成VtTickData
                tick = VtTickData()

                tick.date = dt.strftime('%Y-%m-%d')
                tick.time = dt.strftime('%H:%M:%S.%f')
                tick.datetime = datetime.datetime.strptime(tick.date + ' ' + tick.time, '%Y-%m-%d %H:%M:%S.%f')
    
                tick.symbol = code
                tick.exchange = exchange
                tick.vtSymbol = self.vtCode
                tick.lastPrice = row['vol']
                tick.lastvolume = row['oi_change']
                tick.askPrice1 = row['vol']
                tick.bidPrice1 = row['vol']
                #保存tick数据到数据库
                self.collection.update_many({'datetime':tick.datetime}, {'$set':tick.__dict__}, upsert = True)
            self.updateHistory(date)
            print u'数据更新\n'
        else:
            print u'当天没有数据！！'
            print '\n'

    def end(self):
        ts.close_apis(self.cons)
        sys.exit(0)



if __name__ == '__main__':
    #----- 测试 ------
    test = raw_input('TEST? [y/n]')
    if test == 'y':
        code = 'rb1805'
        exchange = 'SHFE'
        asset = 1
        startDate = '2017-05-16'
        engine = TicksLocalEngine(code, exchange, asset, startDate)
        engine.startWork()
    else:
        #合约代码
        code = raw_input('code[600380]: ')
        if not len(code):
            print u'合约代码不能为空！！'
            sys.exit(0)

        #交易所
        exchange = raw_input('exchange[SSE]: ')
        if not len(exchange):
            print u'交易所不能为空！！'
            sys.exit(0)

        #合约类型
        print u'合约类型：1 商品期货；2 股指期货：回车 A股'
        asset = int(raw_input('asset: '))

        #起始时间
        startDate = raw_input('start date[2017-01-01]: ')
        if not len(startDate):
            print u'起始日期不能为空！！'
            sys.exit(0)
        

        engine = TicksLocalEngine(code, exchange, asset, startDate)
        engine.startWork()
    