#-- coding: utf-8 --

import rqdatac as rq
from rqdatac import *
import pandas as pd
from vnpy.trader.vtObject import VtTickData
import os
from datetime import datetime
from time import time
import re

symbolDict  = {'RB':'rb'}

#账号密码
userName = "license"
password = "OZfNj71Cb6i-eXwOZzuSdHK-U23E1-irpH4EBPwf_RqIgY0-vka35iYmjBot1i2W9eJ4xiZWtrNpxsvy_iY3Il2_YkNjNzW9TVUuFWNp0QNKe0qgO1CSSYDe5uD9ajcN5J7rNtxdagH4Rmfiuv_gHc5bdxxXCnjRH2vZ8JSb2wE=TQFXjsEHPXK2rGTBE1nlgn-BlbI2IvHZmfFsM8tw3jZYATwcUvnXCCGATnAKLIBRnSc1JYVhfm1CUyRdam0vrWeUgebLaPT1rJiXkdQT2WUTwNIB3AY-TVKJciNZzGw0glt02EZXYvYPVlgiqefYVNkLEJ3EApj4i5wsd5C9J48="

#初始化
rq.init(userName, password)

class RQDataService(object):
    def __init__(self):
        super(RQDataService, self).__init__()

    # 下载主力连续Tick数据并保存到csv文件
    def fetchDominantTickToCSVs(self, underlyingSymbol, startDate, endDate):
        # 获取主力合约列表
        dominantList = get_dominant_future(underlyingSymbol, start_date=startDate, end_date=endDate, rule=0)
        if not isinstance(dominantList, pd.Series):
            print '该品种没有上市合约'
            return

        i = 0
        while i < len(dominantList):
            index = dominantList.index[i]
            i += 1
            # RQData标准化合约
            rqSymbol = dominantList[index]
            # vnpy标准化合约
            vtSymbol = self.transformVtSymbol(rqSymbol)

            dt = index.to_pydatetime()
            count = 0
            startTime = time()
            print '=' * 6, vtSymbol, ' ', dt.date(), '=' * 6
            #获取tick
            tickData = rq.get_price(rqSymbol, dt.strftime('%Y-%m-%d'), dt.strftime('%Y-%m-%d'),'tick')
            isDf = isinstance(tickData, pd.DataFrame)
            if isDf:
                # 排除数据有误或者当天没有数据的情况
                instrumentCln = []
                tradingDayCln = []
                calendarDayCln = []
                timeCln = []
                for index, row in tickData.iterrows():
                    # 合约
                    instrumentCln.append(vtSymbol)
                    # 交易日
                    tradingDay = row['trading_date'].strftime('%Y%m%d')
                    tradingDayCln.append(tradingDay)
                    # 实际日期
                    dt = index.to_pydatetime()
                    calendarDay = dt.strftime('%Y%m%d')
                    calendarDayCln.append(calendarDay)
                    # 实际时间
                    theTime = dt.strftime('%H%M%S%f')
                    theTime = theTime[0:len(theTime) - 3]
                    timeCln.append(theTime)
                    count += 1
                if count:
                    # 增加列
                    tickData.insert(0, 'time', timeCln)
                    tickData.insert(0, 'calendarday', calendarDayCln)
                    tickData.insert(0, 'tradingday', tradingDayCln)
                    tickData.insert(0, 'instrument', instrumentCln)
                    # 改名列
                    tickData.rename(columns={'last': 'lastp'}, inplace=True)
                    tickData.rename(columns={'open_interest': 'openinterest'}, inplace=True)
                    tickData.rename(columns={'total_turnover': 'turnover'}, inplace=True)
                    tickData.rename(columns={'a1': 'ask1'}, inplace=True)
                    tickData.rename(columns={'a2': 'ask2'}, inplace=True)
                    tickData.rename(columns={'a3': 'ask3'}, inplace=True)
                    tickData.rename(columns={'a4': 'ask4'}, inplace=True)
                    tickData.rename(columns={'a5': 'ask5'}, inplace=True)
                    tickData.rename(columns={'a1_v': 'asksz1'}, inplace=True)
                    tickData.rename(columns={'a2_v': 'asksz2'}, inplace=True)
                    tickData.rename(columns={'a3_v': 'asksz3'}, inplace=True)
                    tickData.rename(columns={'a4_v': 'asksz4'}, inplace=True)
                    tickData.rename(columns={'a5_v': 'asksz5'}, inplace=True)
                    tickData.rename(columns={'b1': 'bid1'}, inplace=True)
                    tickData.rename(columns={'b2': 'bid2'}, inplace=True)
                    tickData.rename(columns={'b3': 'bid3'}, inplace=True)
                    tickData.rename(columns={'b4': 'bid4'}, inplace=True)
                    tickData.rename(columns={'b5': 'bid5'}, inplace=True)
                    tickData.rename(columns={'b1_v': 'bidsz1'}, inplace=True)
                    tickData.rename(columns={'b2_v': 'bidsz2'}, inplace=True)
                    tickData.rename(columns={'b3_v': 'bidsz3'}, inplace=True)
                    tickData.rename(columns={'b4_v': 'bidsz4'}, inplace=True)
                    tickData.rename(columns={'b5_v': 'bidsz5'}, inplace=True)

                    # 删除列
                    del tickData['trading_date']
                    del tickData['ask2']
                    del tickData['ask3']
                    del tickData['ask4']
                    del tickData['ask5']
                    del tickData['bid2']
                    del tickData['bid3']
                    del tickData['bid4']
                    del tickData['bid5']
                    del tickData['asksz2']
                    del tickData['asksz3']
                    del tickData['asksz4']
                    del tickData['asksz5']
                    del tickData['bidsz2']
                    del tickData['bidsz3']
                    del tickData['bidsz4']
                    del tickData['bidsz5']


                    # 保存数据到csv
                    dirPath = os.getcwd() + '\\CSVs\\RQTick\\' + dt.strftime('%Y') + '\\' + underlyingSymbol + '00' + '\\'
                    if not os.path.exists(dirPath):
                        # 文件夹不存在自动创建文件夹
                        os.makedirs(dirPath)
                    filePath = dirPath + dt.strftime('%Y%m%d') + '.csv'
                    if os.path.exists(filePath):
                        # 旧的文件数据会被删除
                        os.remove(filePath)
                    tickData.to_csv(filePath)

                # 打印进程
                sub = time() - startTime
                print u'用时：', sub, 's'
                print u'数据量：', count, '\n'
                '''
                for index, row in tickData.iterrows():
                    dt = index.to_datetime()
                    # 数据封装成VtTickData
                    tick = VtTickData()
                    tick.date = dt.strftime('%Y-%m-%d')
                    tick.time = dt.strftime('%H:%M:%S.%f')
                    tick.datetime = datetime.datetime.strptime(tick.date + ' ' + tick.time, '%Y-%m-%d %H:%M:%S.%f')
                    tick.symbol = vtSymbol
                    tick.vtSymbol = vtSymbol
                    tick.lastPrice = row['last']
                    tick.lastvolume = row['volume']
                    tick.askPrice1 = row['a1']
                    tick.askVolume1 = row['a1_v']
                    tick.bidPrice1 = row['b1']
                    tick.bidVolume1 = row['b1_v']
                    tick.openPrice = row['open']
                    tick.highPrice = row['high']
                    tick.lowPrice = row['low']
                    tick.lowerLimit = row['limit_down']
                    tick.upperLimit = row['limit_up']
                    tick.openInterest = row['open_interest']
                    tick.preClosePrice = row['prev_close']
                    # 保存tick数据到数据库
                    self.collection.update_many({'datetime': tick.datetime}, {'$set': tick.__dict__}, upsert=True)
                '''

    def transformVtSymbol(self, rqSymbol):
        startSymbol = re.sub("\d", "", rqSymbol)
        endSymbol = re.sub("\D", "", rqSymbol)
        if startSymbol in symbolDict:
            return symbolDict[startSymbol] + endSymbol
        else:
            return rqSymbol



if __name__ == '__main__':
    dtService = RQDataService()
    dtService.fetchDominantTickToCSVs('RB', '2019-1-23', '2019-1-24')