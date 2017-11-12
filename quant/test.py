# -- coding: utf-8 --

import pymongo
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
from datetime import datetime, timedelta

client = pymongo.MongoClient('localhost', 27017)
collection = client[TICK_DB_NAME]['600380.SSE']
flt = {'datetime':{'$gte':datetime.strptime('2017-6-6', '%Y-%m-%d'),
                    '$lt':datetime.strptime('2017-6-7', '%Y-%m-%d')}}
cursor = collection.find(flt).sort('datetime')
for d in cursor:
    print d['datetime']