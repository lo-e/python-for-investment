#-- coding: utf-8 --

import requests
from datetime import datetime
import time
from collections import defaultdict
import os
import csv

main_url = 'https://hist-quote.1tokentrade.cn'
ot_key = 'JfmGSuv1-59r7T9m4-pHPLO63T-BflOru2o' # loe
#ot_key = 'sMJ9QjMU-dYMSKcLu-j05hIU8h-StjPWIEA' # szxbh 18116350794

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
    date = '2019-07-02'
    get_contracts_list(date)
    """

    """
    # 获取bar数据
    contract = 'huobif/eos.usd.q'
    start_month = 4
    since = f'2019-0{start_month}-01'
    until = f'2019-0{start_month+1}-01'
    duration = '1d'

    get_bar_data(contract=contract, since=since, until=until, duration=duration)
    """

    """
    # 获取tick数据
    data_type = 'simple'
    contract = 'huobip/eos.btc'
    date = '2019-07-02'
    get_tick_data(data_type=data_type, contract=contract, date=date)
    """

    #"""
    # 查询具体交易对数据的起始时间
    contract = 'huobip/eos.usdt'
    duration = '5m'
    get_contract_since(contract=contract, duration=duration)
    #"""