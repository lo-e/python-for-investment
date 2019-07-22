import requests
import time
import datetime
import os
import csv

# API
URL_COIN_LIST = 'https://www.cryptocompare.com/api/data/coinlist/'
URL_PRICE = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI_FULL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}'
URL_HIST_PRICE = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym={}&tsyms={}&ts={}&e={}'
URL_HIST_PRICE_DAY = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&limit={}'

""" modify by loe """
URL_HIST_PRICE_DAY_WITH_EXCHANGE = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&limit={}&e={}'

URL_HIST_PRICE_HOUR = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&limit={}'
URL_HIST_PRICE_MINUTE = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&limit={}'
URL_AVG = 'https://min-api.cryptocompare.com/data/generateAvg?fsym={}&tsym={}&e={}'
URL_EXCHANGES = 'https://www.cryptocompare.com/api/data/exchanges'

# FIELDS
PRICE = 'PRICE'
HIGH = 'HIGH24HOUR'
LOW = 'LOW24HOUR'
VOLUME = 'VOLUME24HOUR'
CHANGE = 'CHANGE24HOUR'
CHANGE_PERCENT = 'CHANGEPCT24HOUR'
MARKETCAP = 'MKTCAP'

# DEFAULTS
CURR = 'EUR'
LIMIT = 1440
###############################################################################

def query_cryptocompare(url,errorCheck=True):
    try:
        response = requests.get(url).json()
    except Exception as e:
        print('Error getting coin information. %s' % str(e))
        return None
    if errorCheck and (response.get('Response') == 'Error'):
        print('[ERROR] %s' % response.get('Message'))
        return None
    return response

def format_parameter(parameter):
    if isinstance(parameter, list):
        return ','.join(parameter)
    else:
        return parameter

###############################################################################

def get_coin_list(format=False):
    response = query_cryptocompare(URL_COIN_LIST, False)['Data']
    if format:
        return list(response.keys())
    else:
        return response

# TODO: add option to filter json response according to a list of fields
def get_price(coin, curr=CURR, full=False):
    if full:
        return query_cryptocompare(URL_PRICE_MULTI_FULL.format(format_parameter(coin),
            format_parameter(curr)))
    if isinstance(coin, list):
        return query_cryptocompare(URL_PRICE_MULTI.format(format_parameter(coin),
            format_parameter(curr)))
    else:
        return query_cryptocompare(URL_PRICE.format(coin, format_parameter(curr)))

def get_historical_price(coin, curr=CURR, timestamp=time.time(), exchange='CCCAGG'):
    if isinstance(timestamp, datetime.datetime):
        timestamp = time.mktime(timestamp.timetuple())
    return query_cryptocompare(URL_HIST_PRICE.format(coin, format_parameter(curr),
        int(timestamp), format_parameter(exchange)))

def get_historical_price_day(coin, curr=CURR, limit=LIMIT):
    return query_cryptocompare(URL_HIST_PRICE_DAY.format(coin, format_parameter(curr), limit))

""" modify by loe """
def get_historical_price_day_with_exchange(coin, curr=CURR, limit=LIMIT, exchange='CCCAGG'):
    return query_cryptocompare(URL_HIST_PRICE_DAY_WITH_EXCHANGE.format(coin, format_parameter(curr), limit, exchange))

def get_historical_price_hour(coin, curr=CURR, limit=LIMIT):
    return query_cryptocompare(URL_HIST_PRICE_HOUR.format(coin, format_parameter(curr), limit))

def get_historical_price_minute(coin, curr=CURR, limit=LIMIT):
    return query_cryptocompare(URL_HIST_PRICE_MINUTE.format(coin, format_parameter(curr), limit))

def get_avg(coin, curr=CURR, exchange='CCCAGG'):
    response = query_cryptocompare(URL_AVG.format(coin, curr, format_parameter(exchange)))
    if response:
        return response['RAW']

def get_exchanges():
    response = query_cryptocompare(URL_EXCHANGES)
    if response:
        return response['Data']

"""
print('================== COIN LIST =====================')
print(cryptocompare.get_coin_list())
print(cryptocompare.get_coin_list(True))

print('===================== PRICE ======================')
print(cryptocompare.get_price(coins[0]))
print(cryptocompare.get_price(coins[1], curr='USD'))
print(cryptocompare.get_price(coins[2], curr=['EUR','USD','GBP']))
print(cryptocompare.get_price(coins[2], full=True))
print(cryptocompare.get_price(coins[0], curr='USD', full=True))
print(cryptocompare.get_price(coins[1], curr=['EUR','USD','GBP'], full=True))

print('==================================================')
print(cryptocompare.get_price(coins))
print(cryptocompare.get_price(coins, curr='USD'))
print(cryptocompare.get_price(coins, curr=['EUR','USD','GBP']))

print('==================== HIST PRICE ==================')
print(cryptocompare.get_historical_price(coins[0]))
print(cryptocompare.get_historical_price(coins[0], curr='USD'))
print(cryptocompare.get_historical_price(coins[1], curr=['EUR','USD','GBP']))
print(cryptocompare.get_historical_price(coins[1], 'USD', datetime.datetime.now()))
print(cryptocompare.get_historical_price(coins[2], ['EUR','USD','GBP'], time.time(), exchange='Kraken'))

print('================== HIST PRICE MINUTE ===============')
print(cryptocompare.get_historical_price_minute(coins[0], curr='USD'))
print(cryptocompare.get_historical_price_minute(coins[0], curr='USD', limit=100))

print('================== HIST PRICE HOUR ===============')
print(cryptocompare.get_historical_price_hour(coins[0]))
print(cryptocompare.get_historical_price_hour(coins[0], curr='USD'))
print(cryptocompare.get_historical_price_hour(coins[1], curr=['EUR','USD','GBP']))

print('================== HIST PRICE DAY ================')
print(cryptocompare.get_historical_price_day(coins[0]))
print(cryptocompare.get_historical_price_day(coins[0], curr='USD'))
print(cryptocompare.get_historical_price_day(coins[1], curr=['EUR','USD','GBP']))

print('======================== AVG =====================')
print(cryptocompare.get_avg(coins[0], exchange='Coinbase'))
print(cryptocompare.get_avg(coins[0], curr='USD', exchange='Coinbase'))

print('====================== EXCHANGES =================')
print(cryptocompare.get_exchanges())
"""

# ======= cryptocompareDataService ======
# 下载bar数据
def get_bar_data(coin:str, curr:str, limit:int, exchange:str, duration:str):
    contract = f'{exchange}/{coin}.{curr}'

    result = None
    if duration == '1d':
        result = get_historical_price_day_with_exchange(coin, curr=curr, limit=limit, exchange=exchange)
    if not result:
        return

    data = result['Data']
    # 数据整理
    result_list = []
    for dic in data:
        open_price = dic['open']
        # 过滤掉空的数据
        if not open_price:
            continue

        # 转换时间戳
        timestamp = dic['time']
        datetime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        dic.pop('time')
        dic['datetime'] = datetime_str
        dic['symbol'] = contract
        result_list.append(dic)

    # 写入csv
    contract = contract.replace('/', '.')
    path = os.getcwd() + f'\\CSVs\\cryptocompare\\{contract}\\{duration}\\'
    if not os.path.exists(path):
        # 文件夹不存在自动创建文件夹
        os.makedirs(path)

    TimeFrom = result['TimeFrom']
    TimeFrom_str = time.strftime("%Y-%m-%d", time.localtime(TimeFrom))
    TimeTo = result['TimeTo']
    TimeTo_str = time.strftime("%Y-%m-%d", time.localtime(TimeTo))
    file_path = path + f'{TimeFrom_str}__{TimeTo_str}.csv'
    field_names = ['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volumefrom', 'volumeto']
    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        # 写入csv文件
        writer.writerows(result_list)
if __name__ == '__main__':
    # 下载日线数据
    get_bar_data('EOS', curr='USDT', limit=2000, exchange='OKEX', duration='1d')

    #print(get_historical_price_day_with_exchange('BTC', curr='USDT', limit=2000, exchange='OKEX'))
    #print(get_historical_price('BTC', 'USDT', datetime.datetime.now(), exchange='OKEX'))
