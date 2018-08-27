# -- coding: utf-8 --

import pymongo
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
from vnpy.trader.app.ctaStrategy.ctaBase import DAILY_DB_NAME
from datetime import datetime
from vnpy.trader.app.ctaStrategy.stgEarningManager import stgEarningManager
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas as pd

def backtesting(symbol, dateFrom, dateTo, size, stopPercent, isMulti):
    client = pymongo.MongoClient('localhost', 27017)
    db = client[DAILY_DB_NAME]
    collection = db[symbol + '.TB']
    collection.create_index('datetime')
    dateFlt = {}
    if dateFrom:
        dateFrom = dateFrom + '0101'
        dateFlt['$gte'] = datetime.strptime(dateFrom, '%Y%m%d')
    if dateTo:
        dateTo = dateTo + '1231'
        dateFlt['$lt'] = datetime.strptime(dateTo, '%Y%m%d')

    flt = {}
    if dateFlt:
        flt['datetime'] = dateFlt

    cursor = collection.find(flt).sort('datetime')
    count = 0

    asset = 100000  #资金
    lever = 5       #杠杆
    lastMonth = ''
    monthEarn = 0
    monthGainCount = 0
    monthLossCount = 0
    totalEarn = 0
    lastSymbol = ''
    currentSymbol = ''
    showSymbol = ''
    openPrice = 0
    closePrice = 0
    priceChange = 0
    originPriceChange = 0
    dailyEarn = 0
    originDailyEarn = 0
    lastBuyChange = 0
    lastSellChange = 0
    direction = 0
    directionStr = ''
    dateList = []
    earnList = []
    drawback = 0
    highest = 0

    earningManager = stgEarningManager()
    # 拿到历史记录
    for dic in cursor:
        currentMonth = dic['datetime'].strftime('%Y%m')
        if not lastMonth:
            lastMonth = currentMonth
        if lastMonth and lastMonth != currentMonth:
            # 新的月份
            # 统计月度收益
            if not isMulti:
                print '***************************************', lastMonth, u'本月度收益', monthEarn, u'盈利天数', monthGainCount, u'亏损天数', monthLossCount, '***************************************', '\n'
                test = 0
            lastMonth = currentMonth
            monthEarn = 0
            monthGainCount = 0
            monthLossCount = 0

        # 上一交易日合约代码
        lastSymbol = currentSymbol
        # 当前交易日合约代码
        currentSymbol = dic['vtSymbol']
        if lastSymbol and lastSymbol != currentSymbol:
            # 移仓换月
            if not isMulti:
                print '===============', u'移仓换月', '==============='
                test = 0
            showSymbol = lastSymbol

            collection = db[lastSymbol + '.TB']
            collection.create_index('datetime')
            theCursor = collection.find({'datetime': dic['datetime']})
            for theDic in theCursor:
                openPrice = theDic['open']
                closePrice = theDic['close']
                if not openPrice:
                    openPrice = 0
                else:
                    openPrice = float(openPrice)

                if not closePrice:
                    closePrice = 0
                else:
                    closePrice = float(closePrice)

                priceChange = closePrice - openPrice
                originPriceChange = 0
                if stopPercent:
                    # 设置了止损
                    highPrice = theDic['high']
                    lowPrice = theDic['low']
                    if not highPrice:
                        highPrice = 0
                    else:
                        highPrice = float(highPrice)

                    if not lowPrice:
                        lowPrice = 0
                    else:
                        lowPrice = float(lowPrice)

                    buyStopPrice = openPrice * (1 - stopPercent / 100.0)
                    sellStopPrice = openPrice * (1 + stopPercent / 100.0)
                    if direction > 0 and lowPrice <= buyStopPrice:
                        if not isMulti:
                            print '@@@@@@@@@@@@', u'止损', '@@@@@@@@@@@@'
                            test = 0
                        originPriceChange = priceChange

                        # 止损
                        priceChange = buyStopPrice - openPrice
                        # 止损并反向
                        # priceChange = (buyStopPrice - openPrice) + (buyStopPrice - closePrice)
                    elif direction < 0 and highPrice >= sellStopPrice:
                        if not isMulti:
                            print '@@@@@@@@@@@@', u'止损', '@@@@@@@@@@@@'
                            test = 0
                        originPriceChange = priceChange

                        # 止损
                        priceChange = sellStopPrice - openPrice
                        # 止损并反向
                        # priceChange = (sellStopPrice - openPrice) + (sellStopPrice - closePrice)

        else:
            showSymbol = currentSymbol
            openPrice = dic['open']
            closePrice = dic['close']
            if not openPrice:
                openPrice = 0
            else:
                openPrice = float(openPrice)

            if not closePrice:
                closePrice = 0
            else:
                closePrice = float(closePrice)

            priceChange = closePrice - openPrice
            originPriceChange = 0
            if stopPercent:
                # 设置了止损
                highPrice = dic['high']
                lowPrice = dic['low']
                if not highPrice:
                    highPrice = 0
                else:
                    highPrice = float(highPrice)

                if not lowPrice:
                    lowPrice = 0
                else:
                    lowPrice = float(lowPrice)

                buyStopPrice = openPrice * (1 - stopPercent / 100.0)
                sellStopPrice = openPrice * (1 + stopPercent / 100.0)
                if direction > 0 and lowPrice <= buyStopPrice:
                    if not isMulti:
                        print '@@@@@@@@@@@@', u'止损', '@@@@@@@@@@@@'
                        test = 0
                    originPriceChange = priceChange

                    # 止损
                    priceChange = buyStopPrice - openPrice
                    # 止损并反向
                    # priceChange = (buyStopPrice - openPrice) + (buyStopPrice - closePrice)
                elif direction < 0 and highPrice >= sellStopPrice:
                    if not isMulti:
                        print '@@@@@@@@@@@@', u'止损', '@@@@@@@@@@@@'
                        test = 0
                    originPriceChange = priceChange

                    # 止损
                    priceChange = sellStopPrice - openPrice
                    # 止损并反向
                    # priceChange = (sellStopPrice - openPrice) + (sellStopPrice - closePrice)

        # 每日收益
        space = int((asset * lever) / (openPrice * size))    #开仓数量
        dailyEarn = priceChange * direction * size * space
        if originPriceChange:
            originDailyEarn = originPriceChange * direction * size * space

        # 月度收益统计
        monthEarn += dailyEarn
        totalEarn += dailyEarn

        # 统计回撤
        highest = max(highest, totalEarn)
        drawback = max(drawback, (highest - totalEarn))

        if dailyEarn > 0:
            monthGainCount += 1
        elif dailyEarn < 0:
            monthLossCount += 1
        # 打印详情
        if not isMulti:
            #'''
            print dic['datetime'], showSymbol, u'开盘', openPrice, u'收盘', closePrice
            print u'涨跌', priceChange, u'前交易日多头增减', lastBuyChange, u'前交易日空头增减', lastSellChange, directionStr, u'盈亏', priceChange * direction, 'x', size, 'x', space, '=', dailyEarn
            if originPriceChange:
                print u'未止损盈亏：', originDailyEarn
            print u'持仓数量：', space
            print u'月度收益累计：', monthEarn
            print u'月度盈利天数：', monthGainCount
            print u'月度亏损天数：', monthLossCount
            print u'总收益：', totalEarn
            print u'最大回撤：', drawback
            print '\n'
            #'''

        if not isMulti:
            '''
            # 保存记录到文件
            fileName = 'daily_' + symbol
            content = OrderedDict()
            content['日期'] = dic['datetime'].strftime('%Y-%m-%d')
            content['合约代码'] = showSymbol
            content['开盘'] = openPrice
            content['收盘'] = closePrice
            content['涨跌'] = priceChange
            content['前交易日多头增减'] = lastBuyChange
            content['前交易日空头增减'] = lastSellChange
            if direction == 1:
                content['交易方向'] = 'buy'
            elif direction == -1:
                content['交易方向'] = 'sell'
            content['持仓数量'] = space
            content['盈亏'] = '%.2f X %d X %d = %.2f' % (priceChange*direction, size, space, dailyEarn)
            content['月度收益累计'] = monthEarn
            content['月度盈利天数'] = monthGainCount
            content['月度亏损天数'] = monthLossCount
            content['总交易日'] = count + 1
            content['总收益'] = totalEarn
            earningManager.updateDailyEarning(fileName, content)
            '''

        dateList.append(dic['datetime'])
        earnList.append(totalEarn)

        lastBuyChange = dic['buyInterestChange']
        lastSellChange = dic['sellInterestChange']
        direction = 0
        directionStr = ''
        if lastBuyChange > lastSellChange:
            direction = 1
            directionStr = u'多'
        elif lastBuyChange < lastSellChange:
            direction = -1
            directionStr = u'空'

        count += 1


    # 统计月度收益
    if not isMulti:
        print '***************************************', lastMonth, u'本月度收益', monthEarn, u'盈利天数', monthGainCount, u'亏损天数', monthLossCount, '***************************************', '\n'

    print '\n'
    print u'总交易日：', count
    print u'总收益：', totalEarn
    print u'最大回撤：', drawback
    print u'止损参数：', stopPercent
    print '\n'

    # 画图
    if not isMulti:
        df = pd.DataFrame.from_dict({'earn': earnList})
        df.index = dateList
        df['earn'].plot()
        plt.show()

def startDailyBacktesting():
    symbol = raw_input(u'合约代码：')
    someDate = raw_input(u'是否指定日期（1.是 2.否）：')
    dateFrom = ''
    dateTo = ''
    if someDate:
        dateFrom = raw_input(u'开始年份：')
        dateTo = raw_input(u'结束年份：')

    size = int(raw_input(u'每手数量：'))

    isStop = raw_input(u'是否止损（1.是 2.否）：')
    if isStop and isStop == '1':
        multi = raw_input(u'是否优化止损（1.是 2.否）：')
        if multi and multi == '1':
            start = float(raw_input(u'start：'))
            end = float(raw_input(u'end：'))
            step = float(raw_input(u'step：'))

            stopPercent = start
            while stopPercent <= end:
                backtesting(symbol, dateFrom, dateTo, size, stopPercent, True)
                stopPercent += step

        elif multi and multi == '2':
            stopPercent = float(raw_input(u'止损百分比：'))
            backtesting(symbol, dateFrom, dateTo, size, stopPercent, False)
        else:
            print u'输入有误！'
    else:
        backtesting(symbol, dateFrom, dateTo, size, 0, False)

if __name__ == '__main__':
    startDailyBacktesting()
