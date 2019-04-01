#-- coding: utf-8 --

import tushare as ts
from vnpy.trader.vtObject import VtBarData, VtTickData
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from vnpy.trader.app.ctaStrategy.ctaBase import (MINUTE_DB_NAME,
                                                 DAILY_DB_NAME,
                                                 TICK_DB_NAME)
"""
IFL.CFX    IFL      沪深300期货当月
IC.CFX     IC       CFFEX中证500期货
IHL.CFX    IHL      上证50期货当月连续
ALL.SHF    ALL      沪铝连续
RBL.SHF    RBL      螺纹钢连续
IL.DCE     IL       铁矿石连续
HCL.SHF    HCL      热轧卷板连续
SML.ZCE    SML      锰硅连续
JML.DCE    JML      焦煤连续
JL.DCE     JL       焦炭连续
ZCL.ZCE    ZCL      动力煤连续
TAL.ZCE    TAL      PTA连续
"""

symbolDict = {'IFL.CFX':'IF',
              'IC.CFX':'IC',
              'IHL.CFX':'IH',
              'ALL.SHF':'AL',
              'RBL.SHF':'RB',
              'IL.DCE':'I',
              'HCL.SHF':'HC',
              'SML.ZCE':'SM',
              'JML.DCE':'JM',
              'JL.DCE':'J',
              'ZCL.ZCE':'ZC',
              'TAL.ZCE':'TA'}

client = MongoClient('localhost', 27017)
dbMinute = client[MINUTE_DB_NAME]
dbDaily = client[DAILY_DB_NAME]
dbTick = client[TICK_DB_NAME]

token = 'e4e657ed6666c850935080e1ef31b4c5f4d8e2ca1eb717a2afe36d51'
ts.set_token(token)
pro = ts.pro_api()

# 查看tushare主力连续合约代码
def fetchMainTsSymbol():
    exchangeList = ['CFFEX', 'SHFE', 'DCE', 'CZCE', 'INE']
    for exchange in exchangeList:
        df = pro.fut_basic(exchange=exchange, fut_type='2', fields='ts_code,symbol,name')
        print df

# 下载主力连续日线数据
def downloadDailyData(tsSymbol):
    vtSymbol = symbolDict[tsSymbol] + '88.TS'
    cl = dbDaily[vtSymbol]
    cl.ensure_index([('datetime', ASCENDING)], unique=True)  # 添加索引
    year = 2001
    currentYear = datetime.now().year
    dataYearList = []
    while year <= currentYear:
        startDate = str(year) + '0101'
        endDate = str(year+1) + '0101'
        df = pro.fut_daily(ts_code=tsSymbol, start_date=startDate, end_date=endDate)
        for index, row in df.iterrows():
            if not year in  dataYearList:
                dataYearList.append(year)

            bar = generateVtBar(row, vtSymbol)
            d = bar.__dict__
            flt = {'datetime': bar.datetime}
            cl.replace_one(flt, d, True)

        year += 1
    print '%s\t数据下载完成\t%s' % (vtSymbol, dataYearList)

# 生成VtBarData
def generateVtBar(row, symbol):
    """生成K线"""
    bar = VtBarData()

    bar.symbol = symbol
    bar.vtSymbol = symbol
    bar.open = row['open']
    bar.high = row['high']
    bar.low = row['low']
    bar.close = row['close']
    bar.volume = row['vol']
    bar.datetime = datetime.strptime(row['trade_date'], '%Y%m%d')
    bar.date = bar.datetime.strftime("%Y%m%d")
    bar.time = bar.datetime.strftime("%H:%M:%S")

    return bar

if __name__ == '__main__':
    #fetchMainTsSymbol()

    """
    tsSymbolList = ['IFL.CFX', 'IC.CFX', 'IHL.CFX', 'ALL.SHF', 'RBL.SHF', 'IL.DCE', 'HCL.SHF', 'SML.ZCE', 'JML.DCE', 'JL.DCE', 'ZCL.ZCE', 'TAL.ZCE']
    for tsSymbol in tsSymbolList:
        downloadDailyData(tsSymbol)
    """
    downloadDailyData('TAL.ZCE')



