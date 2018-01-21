#-- coding: utf-8 --

import pymongo
from datetime import datetime
from vnpy.trader.vtObject import VtTickData
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
import os
import csv
from time import time, sleep

class csvsLocalEngine(object):
    def __init__(self):
        super(csvsLocalEngine, self).__init__()
        # 项目路径
        self.walkingDir = 'CSVs'
        # 获取数据库
        client = pymongo.MongoClient('localhost', 27017)
        self.db = client[TICK_DB_NAME]

        #self.collection.create_index('datetime')

    def startWork(self):
        # 数据库collection
        collection = self.db['rb1805.TB']

        testDate = None
        testStartTime = 0
        testEndTime = 0
        for root, subdirs, files in os.walk(self.walkingDir):
            for theFile in files:
                if '.csv' in theFile:
                    # 载入文件内容
                    filePath = root + '\\' + theFile
                    with open(filePath, 'r') as f:
                        reader = csv.DictReader(f)

                        for row in reader:
                            # 创建VtTickData对象
                            tick = VtTickData()
                            tick.vtSymbol = row['instrument']
                            tick.lastPrice = row['lastp']
                            tick.volume = row['volume']
                            tick.openInterest = row['openinterest']
                            tick.askPrice1 = row['ask1']
                            tick.askVolume1 = row['asksz1']
                            tick.bidPrice1 = row['bid1']
                            tick.bidVolume1 = row['bidsz1']

                            tick.date = row['calendarday']
                            temp = datetime.strptime(row['time'], '%H%M%S%f')
                            tick.time = temp.strftime('%H:%M:%S.%f')
                            tick.datetime = datetime.strptime(tick.date + ' ' + tick.time, '%Y%m%d %H:%M:%S.%f')
                            '''
                            # 数据库collection
                            collection = self.db[tick.vtSymbol + '.TB']
                            '''

                            # 保存tick到数据库
                            collection.update_one({'datetime': tick.datetime}, {'$set': tick.__dict__}, upsert = True)

                            print tick.datetime
                            if testDate != tick.datetime.date():
                                testEndTime = time()
                                if testStartTime:
                                    sub = testEndTime - testStartTime
                                    print u'用时：', sub, 's\n'

                                testDate = tick.datetime.date()
                                testStartTime = time()
                                print '='*6, tick.vtSymbol, ' ', tick.datetime.date(), '='*6
                                sleep(2)


if __name__ == '__main__':
    engine = csvsLocalEngine()
    engine.startWork()
