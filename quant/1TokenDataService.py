#-- coding: utf-8 --

import requests
from datetime import datetime, timedelta
import time
from collections import defaultdict
import os
import csv
from CSVsToLocal import CSVs1TokenBarLocalEngine
from BarToLocal import BarLocalEngine

main_url = 'https://hist-quote.1tokentrade.cn'
ot_key = 'JfmGSuv1-59r7T9m4-pHPLO63T-BflOru2o' # loe
#ot_key = 'sMJ9QjMU-dYMSKcLu-j05hIU8h-StjPWIEA' # szxbh 18116350794
#ot_key = 'i9XIu2q9-aAOSuHVC-9HyL8fuq-Wdc3JPEv'  # token8122 17174208122
#ot_key = 'Hx4oGmxw-qjywlk6f-QYqAjw4c-g6SN7X03'  # token8121 17174208118
#ot_key = 'LSjHuwNb-f1B6uafF-omcbhq6d-4NdFNp1n'  # token8117 17174208117

# ====== 获取支持的合约列表 ======
# date：'YYYY-MM-DD'
def get_contracts_list(date:str):
    url = f'{main_url}/ticks/contracts?date={date}'
    resp = requests.get(url, headers={}, params={})
    data = resp.json()

    # 数据整理
    dic = defaultdict(list)
    for contract in data:
        array = contract.split('/')
        if len(array) < 2:
            print('Error !!')
            exit(0)
        exchange = array[0]
        symbol = array[1]
        esList = dic[exchange]
        esList.append(symbol)
    result_list = []
    for key, value in dic.items():
        for symbol in value:
            result_list.append({'exchange': key, 'symbol': symbol})
        result_list.append({'exchange': '', 'symbol': ''})

    # 写入csv
    path = os.getcwd()
    file_path = path + '\\CSVs\\1Token\\' + 'contracts.csv'
    field_names = ['exchange', 'symbol']
    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        # 写入csv文件
        writer.writerows(result_list)


# ====== 获取bar数据 ======
# contract：'huobif/btc.usd.t'
# since：'YYYY-MM-DD'
# until：'YYYY-MM-DD'
# duratioon：'1m/5m/15m/30m/1h/1d'
def get_bar_data(contract:str, since:str, until:str, duration:str):
    url = f'{main_url}/candles?contract={contract}&since={since}&until={until}&duration={duration}&format=json'
    header = {'ot-key': ot_key}
    resp = requests.get(url, headers=header, params={})
    data = resp.json()

    # 数据整理
    result_list = []
    for dic in data:
        # 转换时间戳
        timestamp = dic['timestamp']
        datetime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        dic.pop('timestamp')
        dic['datetime'] = datetime_str
        dic['symbol'] = contract
        result_list.append(dic)

    if not len(result_list):
        return

    # 写入csv
    contract = contract.replace('/', '.')
    path = os.getcwd() + f'\\CSVs\\1Token\\{contract}\\{duration}\\'
    if not os.path.exists(path):
        # 文件夹不存在自动创建文件夹
        os.makedirs(path)
    file_path = path + f'{since}__{until}.csv'
    field_names = ['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume']
    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        # 写入csv文件
        writer.writerows(result_list)


# ====== 获取tick数据 ======
# data_type：'simple' \ 'full'
# contract：'huobif/btc.usd.t'
# date：'YYYY-MM-DD'
def get_tick_data(data_type:str, contract:str, date:str):
    url = f'{main_url}/ticks/{data_type}?contract={contract}&date={date}'
    header = {'ot-key': ot_key}
    resp = requests.get(url, headers=header, params={})
    data = resp.json()
    print(data)


# ====== 查询具体交易对数据的起始时间 ======
# contract：'huobif/btc.usd.t'
# duratioon：'1m/5m/15m/30m/1h/1d'
def get_contract_since(contract:str, duration:str):
    url = f'{main_url}/candles/since?contract={contract}&duration={duration}&format=json'
    resp = requests.get(url, headers={}, params={})
    data = resp.json()
    timestamp = data['since']
    date = datetime.fromtimestamp(timestamp)
    print(date)

if __name__ == '__main__':
    """
    # 获取支持的合约列表
    date = '2019-09-02'
    get_contracts_list(date)
    """

    #"""
    # 获取bar数据
    contractList = ['okef/btc.usd.q', 'okef/eth.usd.q', 'okef/eos.usd.q', 'okswap/btc.usd.td', 'okswap/eth.usd.td', 'okswap/eos.usd.td']
    duration = '1m'
    start = datetime.now() - timedelta(1)
    start = datetime(start.year, start.month, start.day)
    until = datetime.now() - timedelta(1)
    until = datetime(until.year, until.month, until.day)
    
    since = start
    while since <= until:
        for contract in contractList:
            print(f'下载数据：{since}\t{contract}')
            get_bar_data(contract=contract, since=datetime.strftime(since, '%Y-%m-%d'), until=datetime.strftime(since + timedelta(1), '%Y-%m-%d'), duration=duration)
        since += timedelta(1)

    # 1m数据入数据库
    print('\n====== 1m数据入数据库 ======')
    engine = CSVs1TokenBarLocalEngine(duration='1m')
    engine.startWork()

    # 1m数据合成Daily数据
    print('\n====== 1m数据合成Daily数据 ======')
    engine = BarLocalEngine(duration='1m')
    start_date = datetime.strftime(start, '%Y-%m-%d')
    end_date = datetime.strftime(datetime.now()+timedelta(1), '%Y-%m-%d')
    for contract in contractList:
        elements = contract.split('/')
        symbol = '.'.join([elements[-1], elements[0]]).upper()
        engine.Crypto_1Min_Daily(symbol=symbol, start_date=start_date, end_date=end_date)
    #"""

    """
    # 获取tick数据
    data_type = 'simple'
    contract = 'okef/btc.usd.q'
    date = '2019-08-27'
    get_tick_data(data_type=data_type, contract=contract, date=date)
    """

    """
    # 查询具体交易对数据的起始时间
    contract = 'okef/btc.usd.q'
    duration = '1h'
    get_contract_since(contract=contract, duration=duration)
    """

    """
    # 获取bar数据
    contractList = ['okswap/btc.usd.td', 'okswap/eth.usd.td', 'okswap/eos.usd.td']
    duration = '1m'
    start = datetime(2019, 8, 7)
    until = datetime.now() - timedelta(1)
    until = datetime(until.year, until.month, until.day)

    since = start
    while since <= until:
        for contract in contractList:
            print(f'下载数据：{since}\t{contract}')
            get_bar_data(contract=contract, since=datetime.strftime(since, '%Y-%m-%d'),
                         until=datetime.strftime(since + timedelta(1), '%Y-%m-%d'), duration=duration)
        since += timedelta(1)
    """
    """
    # 1m数据入数据库
    print('\n====== 1m数据入数据库 ======')
    engine = CSVs1TokenBarLocalEngine(duration='1m')
    engine.startWork()
    """

    """
    # 1m数据合成Daily数据
    print('\n====== 1m数据合成Daily数据 ======')
    contractList = ['okswap/btc.usd.td', 'okswap/eth.usd.td', 'okswap/eos.usd.td']
    engine = BarLocalEngine(duration='1m')
    start = datetime(2019, 8, 1)
    start_date = datetime.strftime(start, '%Y-%m-%d')
    end_date = datetime.strftime(datetime.now() + timedelta(1), '%Y-%m-%d')
    for contract in contractList:
        elements = contract.split('/')
        symbol = '.'.join([elements[-1], elements[0]]).upper()
        engine.Crypto_1Min_Daily(symbol=symbol, start_date=start_date, end_date=end_date)
    """