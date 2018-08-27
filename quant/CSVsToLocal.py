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

class csvsLocalEngine(object):
    def __init__(self, type, night):
        super(csvsLocalEngine, self).__init__()
        # 合约类型，不同品种期货交易时间特别是夜盘时间会有所差别，为了剔除无效数据而设置 1、商品期货  2、股指期货
        self.dataType = type
        # 夜盘时间类型
        self.night = night
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
                dirName = ''
                currentDate = None
                currentSymbol = ''
                count = 0

                # 确定合约【由文件夹名称决定，因为主力合约只能在文件夹名称中确定】
                if '\\' in root:
                    currentSymbol =  root.split('\\')[-1]
                    if not currentSymbol or (not currentSymbol.endswith('00')):
                        continue
                    currentSymbol = currentSymbol  + '.TB'

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
                                print u'时间转换异常：%s' % timeStr
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
                            collection = self.db[currentSymbol]
                            collection.create_index('datetime')
                            if fakeData:
                                print t
                                print u'【剔除无效数据】'
                                # 删除已保存的数据库数据
                                flt = {'datetime': theDatetime}
                                cursor = collection.find(flt)
                                if cursor.count():
                                    print u'【剔除无效‘数据库’数据】'
                                collection.delete_many(flt)
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
                            tick.date = theDate
                            tick.time = theTime
                            tick.datetime = theDatetime
                            # 保存tick到数据库
                            collection.update_many({'datetime': tick.datetime}, {'$set': tick.__dict__}, upsert = True)
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
    type = int(raw_input(u'合约类型【1、商品 2、股指】：'))
    if type != 1 and type != 2 :
        print '输入有误'
        exit(0)

    if type == 1:
        night = int(raw_input(u'夜盘时间类型【0、无 1、夜间23:00 2、凌晨1:00 3、凌晨2:30】：'))
        if night != 0 and night != 1 and night != 2 and night != 3:
            print '输入有误'
            exit(0)
    engine = csvsLocalEngine(type, night)
    engine.startWork()
