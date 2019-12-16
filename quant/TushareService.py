#-- coding: utf-8 --

import tushare as ts
from vnpy.trader.object import BarData, TickData
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
from vnpy.app.cta_strategy.base import (MINUTE_DB_NAME,
                                        DAILY_DB_NAME,
                                        TICK_DB_NAME)
from vnpy.trader.constant import Exchange
from copy import copy
from pymongo import MongoClient, ASCENDING, DESCENDING
from vnpy.app.cta_strategy.base import DAILY_DB_NAME, DOMINANT_DB_NAME
import traceback
from time import sleep
import re
from vnpy.app.cta_strategy.base import TRANSFORM_SYMBOL_LIST

SYMBOL_EXCHANGE_MAP = {'RB':'SHF',
                       'HC':'SHF',
                       'SM':'ZCE',
                       'J':'DCE',
                       'ZC':'ZCE',
                       'TA':'ZCE'}

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

client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=600)
client.server_info()
dbDominant = client[DOMINANT_DB_NAME]
dbDaily = client[DAILY_DB_NAME]

token = '51b19d10cd7d6370c19c4a12087b2eff8c5eaeb50058b84bd4c8117a'
ts.set_token(token)
pro = ts.pro_api()

class TushareSymbolData:
    ts_code:str = ''        # tushare合约代码
    symbol:str = ''         # 去掉交易所的合约代码
    exchange = ''           # 交易所
    name:str = ''           # 简称
    fut_code = ''           # 合约产品代码【例如RB、IF】
    multiplier = ''         # 合约乘数
    trade_unit = ''         # 交易计量单位
    per_unit = ''           # 交易单位(每手)
    quote_unit = ''         # 报价单位
    quote_unit_desc = ''    # 最小报价单位说明
    d_mode_desc = ''        # 交割方式说明
    list_date = ''          # 上市日期
    delist_date = ''        # 最后交易日期
    d_month = ''            # 交割月份
    last_ddate = ''         # 最后交割日
    trade_time_desc = ''    # 交易时间说明

class TradeCalendarData:
    exchange = ''
    cal_date = ''
    is_open = 0         # 0休市 1交易

# 交易所交易日历
# exchange：SHFE 上期所 DCE 大商所 CFFEX中金所 CZCE郑商所 INE上海国际能源交易所
# start_date：'20190101'
# end_date：'20191231'
def fetchTradeDateList(exchange:str='', start_date:str='', end_date:str=''):
    if not exchange:
        return []

    df = pro.trade_cal(exchange=exchange, start_date=start_date, end_date=end_date, is_open=1)
    result_list = []
    for index, row in df.iterrows():
        cal_datetime = datetime.strptime(row['cal_date'], '%Y%m%d')
        result_list.append(cal_datetime)
    return result_list

# 获取下一个交易日
def fetchNextTradeDate(exchange:str='', from_date:datetime=None):
    if not exchange:
        return None

    if not from_date:
        return None

    start_date = from_date.strftime('%Y%m%d')
    end_date = (from_date + timedelta(days=30)).strftime('%Y%m%d')
    date_list = fetchTradeDateList(exchange=exchange, start_date=start_date, end_date=end_date)
    result = None
    for the_date in sorted(date_list):
        if the_date > from_date:
            result = the_date
            break
    return result

# 查看所有合约代码
def fetchSymbolList():
    exchangeList = ['CFFEX', 'SHFE', 'DCE', 'CZCE', 'INE']
    data_list = []
    for exchange in exchangeList:
        #df = pro.fut_basic(exchange=exchange, fields='ts_code,symbol,name')
        df = pro.fut_basic(exchange=exchange)
        for index, row in df.iterrows():
            data_dic = dict(row)
            symbol_data = TushareSymbolData()
            symbol_data.ts_code = data_dic.get('ts_code', '')
            symbol_data.symbol = data_dic.get('symbol', '')
            symbol_data.exchange = data_dic.get('exchange', '')
            symbol_data.name = data_dic.get('name', '')
            symbol_data.fut_code = data_dic.get('fut_code', '')
            symbol_data.multiplier = data_dic.get('multiplier', '')
            symbol_data.trade_unit = data_dic.get('trade_unit', '')
            symbol_data.per_unit = data_dic.get('per_unit', '')
            symbol_data.quote_unit = data_dic.get('quote_unit', '')
            symbol_data.quote_unit_desc = data_dic.get('quote_unit_desc', '')
            symbol_data.d_mode_desc = data_dic.get('d_mode_desc', '')
            symbol_data.list_date = data_dic.get('list_date', '')
            symbol_data.delist_date = data_dic.get('delist_date', '')
            symbol_data.d_month = data_dic.get('d_month', '')
            symbol_data.last_ddate = data_dic.get('last_ddate', '')
            symbol_data.trade_time_desc = data_dic.get('trade_time_desc', '')

            startSymbol = re.sub("\d", "", symbol_data.symbol)
            if startSymbol in TRANSFORM_SYMBOL_LIST.keys():
                endSymbol = re.sub("\D", "", symbol_data.symbol)
                if endSymbol.startswith('0'):
                    replace = 2
                else:
                    replace = 1
                symbol_data.symbol = startSymbol + str(replace) + endSymbol

            data_list.append(symbol_data)
    return data_list

# 下载日线数据
# start = '20190101     end = '20191231'
def downloadDailyData(ts_code:str, start:str, end:str, to_database:bool=False) -> (list, str):
    symbol = ts_code
    temp = ts_code.split('.')
    symbol = temp[0]

    df = pro.fut_daily(ts_code=ts_code, start_date=start, end_date=end).sort_values(by="trade_date", ascending=True)
    bar_list = []
    date_from = None
    date_to = None
    for index, row in df.iterrows():
        bar = generateVtBar(row, symbol)
        bar_list.append(bar)
        if not date_from:
            date_from = bar.datetime
        date_to  = bar.datetime

    msg = ''
    if len(bar_list):
        if to_database:
            # 保存数据库
            collection = dbDaily[bar.symbol]
            for bar in bar_list:
                collection.update_many({'datetime': bar.datetime}, {'$set': bar.__dict__}, upsert=True)
            msg = f'{ts_code}\t数据下载并保存数据库完成【{len(bar_list)}】\t{date_from} - {date_to}'
        else:
            msg = f'{ts_code}\t数据下载完成【{len(bar_list)}】\t{date_from} - {date_to}'
    else:
        msg = f'{ts_code}\t数据下载空！！\t{start} - {end}'

    return bar_list, msg

# 生成VtBarData
def generateVtBar(row, symbol):
    """生成K线"""
    bar = BarData(gateway_name = '', symbol = symbol, exchange = Exchange.LOCAL, datetime = None, endDatetime = None)
    bar.datetime = datetime.strptime(row['trade_date'], '%Y%m%d')
    bar.open_price = row['open']
    bar.high_price = row['high']
    bar.low_price = row['low']
    bar.close_price = row['close']
    bar.volume = row['vol']
    bar.open_interest = row['oi']
    bar.exchange = bar.exchange.value
    return bar

# 判断主力合约并存入数据库，指定单个日期
def get_and_save_dominant_symbol(symbol:str, target_date:datetime) -> (str, str):
    # 获取合约列表
    all_symbol_list = fetchSymbolList()

    # 获取目标代码还在交易的所有合约数据
    target_symbol_data_list = []
    for symbol_data in all_symbol_list:
        if symbol_data.list_date and symbol_data.delist_date:
            start_trade_date = datetime.strptime(symbol_data.list_date, '%Y%m%d')
            last_trade_date = datetime.strptime(symbol_data.delist_date, '%Y%m%d')
            if symbol == symbol_data.fut_code and start_trade_date <= target_date and last_trade_date >= target_date:
                target_symbol_data_list.append(symbol_data)

    # 数据库获取最新主力合约代码
    collection = dbDominant[symbol]
    cursor = collection.find().sort('date', direction=DESCENDING)
    last_dominant_symbol = ''
    last_dominant_date = None
    for dic in cursor:
        last_dominant_symbol = dic['symbol']
        last_dominant_date = dic['date']
        break

    if last_dominant_date > target_date:
        return ('', f'{last_dominant_symbol} -> {target_date}')

    # 下载当前主力Daily_Bar数据
    target_date_str = target_date.strftime('%Y%m%d')
    last_dominant_bar = None
    if last_dominant_symbol:
        for symbol_data in target_symbol_data_list:
            if symbol_data.symbol == last_dominant_symbol:
                bar_list, msg = downloadDailyData(ts_code=symbol_data.ts_code, start=target_date_str, end=target_date_str)
                if not bar_list:
                    return ('', f'{symbol_data.ts_code}\t{target_date} Bar数据缺失，无法判断主力！')
                last_dominant_bar = bar_list[0]
                break

    # 判断主力合约
    new_dominant_bar = None
    new_dominant_symbol_data = None
    if last_dominant_symbol:
        # 若合约持仓量大于当前主力合约持仓量的1.1倍时，新主力产生
        for symbol_data in target_symbol_data_list:
            if symbol_data.symbol == last_dominant_symbol:
                continue

            ts_code = symbol_data.ts_code
            # 下载Daily_Bar数据
            bar_list, msg = downloadDailyData(ts_code=ts_code, start=target_date_str, end=target_date_str)
            if not bar_list:
                return ('', f'{ts_code}\t{target_date} Bar数据缺失，无法判断主力！')

            bar = bar_list[0]
            if bar.open_interest > last_dominant_bar.open_interest * 1.1:
                if new_dominant_bar:
                    return ('', f'{symbol}\t{target_date}出现不止一个新主力合约，检查代码！！')
                new_dominant_bar = copy(bar)
                new_dominant_symbol_data = symbol_data

    else:
        # 持仓量最大的为下一交易日主力
        max_open_interest = 0
        for symbol_data in target_symbol_data_list:
            ts_code = symbol_data.ts_code
            # 下载Daily_Bar数据
            bar_list, msg = downloadDailyData(ts_code=ts_code, start=target_date_str, end=target_date_str)
            if not bar_list:
                return ('', f'{ts_code}\t{target_date} Bar数据缺失，无法判断主力！')

            bar = bar_list[0]
            if bar.open_interest > max_open_interest:
                max_open_interest = bar.open_interest
                new_dominant_bar = copy(bar)
                new_dominant_symbol_data = symbol_data

    if new_dominant_bar:
        # 出现新主力，保存数据库
        next_trade_date = fetchNextTradeDate(exchange=new_dominant_symbol_data.exchange, from_date=target_date)
        if next_trade_date:
            dominant_dict = {'date': next_trade_date,
                             'symbol': new_dominant_bar.symbol}
            collection.update_many({'date': next_trade_date}, {'$set': dominant_dict}, upsert=True)
            return (new_dominant_bar.symbol, f'{new_dominant_bar.symbol} -> {target_date}')
        else:
            return ('', '获取下一个交易日出错，检查代码！！')
    else:
        if last_dominant_symbol:
            return ('', f'{last_dominant_symbol} -> {target_date}')
        else:
            return ('', f'数据库没有存档记录，并且找不到新主力合约，检查代码！！')

# 判断主力合约并存入数据库，指定起始日期
def get_and_save_dominant_symbol_from(symbol:str, from_date:datetime):
    today_date = datetime.strptime(datetime.now().strftime('%Y%m%d'), '%Y%m%d')
    target_date = from_date
    while target_date <= today_date:
        try:
            new_dominant, msg = get_and_save_dominant_symbol(symbol=symbol, target_date=target_date)
            if new_dominant:
                # 有新的主力产生
                print(f'{msg}\t新主力')
            else:
                # 没有新主力产生
                print(msg)
            target_date += timedelta(days=1)
        except:
            msg = traceback.format_exc()
            if '每分钟' in msg:
                print(msg)
                sleep(60)
            else:
                raise (msg)

def trasform_tscode(symbol:str):
    ts_code = symbol.upper()
    startSymbol = re.sub("\d", "", ts_code)
    if startSymbol in SYMBOL_EXCHANGE_MAP.keys():
        ts_code = ts_code + f'.{SYMBOL_EXCHANGE_MAP[startSymbol]}'
    return ts_code

def standard_daily_datetime(target_datetime:datetime):
    return datetime.strptime(target_datetime.strftime('%Y%m%d'), '%Y%m%d')

if __name__ == '__main__':
    """
    # 下载Daily_Bar数据
    bar_list, msg = downloadDailyData(ts_code='RBL.SHF', start='', end='')
    print(msg)
    """

    """
    # 添加空的Daily_Bar数据到数据库
    symbol = 'A0000'
    the_datetime = datetime.strptime('2019-12-13', '%Y-%m-%d')
    bar = BarData(gateway_name='', symbol=symbol, exchange='', datetime=the_datetime, endDatetime=None)
    collection = dbDaily[bar.symbol]
    collection.insert_one(bar.__dict__)
    """

    """
    # 添加空的Dominant数据到数据库
    underline = 'HC'
    symbol = 'HC2005'
    date = datetime.strptime('2019-12-13', '%Y-%m-%d')
    collection = dbDominant[underline]
    collection.insert_one({'symbol':symbol,
                           'date':date})
    """

