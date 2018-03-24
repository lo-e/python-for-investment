# -- coding: utf-8 --

import pymongo
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
from datetime import datetime


if __name__ == '__main__':
    client = pymongo.MongoClient('localhost', 27017)
    db = client[TICK_DB_NAME]
    collection = db['rb1805']
    collection.create_index('datetime')

    # data ={'testId':2, 'testData':'a'}
    # collection.update_many({'testId': 1}, {'$set': data}, upsert = True)
    startDatetime = datetime.strptime('2018-03-14 22:58:23', '%Y-%m-%d %H:%M:%S')
    endDatetime = datetime.strptime('2018-03-14 22:58:26', '%Y-%m-%d %H:%M:%S')
    flt = {'datetime': {'$gte': startDatetime,
                        '$lt': endDatetime}}
    cursor = collection.find(flt)
    cursor.skip(2)
    index = 0
    while index < cursor.count()-2:
        print cursor[index]['datetime']
        index += 1
