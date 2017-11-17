# -*- coding: utf-8 -*-

import futuquant as ft
from QuoteHandler import *
import time

'''
定义变量
'''
#服务器ip
#api_svr_ip = '119.29.141.202'
api_svr_ip = '127.0.0.1'

#服务器端口
api_svr_port = 11111

#交易密码
#password = 123456
password = 970769

#股票代码
#code = 'HK.00700'
code = 'SH.600380'

#股票市场
#market = 'HK'
market = 'SH'

#交易环境，实盘交易：0 模拟环境：1（美股不支持模拟）
trade_env = 1

'''
行情上下文
'''
#实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host = api_svr_ip, port = api_svr_port)
#print(quote_ctx.get_global_state())

'''
异步控制
'''
#开启异步数据接收
quote_ctx.start()

#停止异步数据接受
#quote_ctx.stop()

#设置用于异步处理数据的回调对象
#quote_ctx.set_handler(handler)

'''
高频行情订阅
'''
#摆盘
#quote_ctx.subscribe(code, 'ORDER_BOOK', push = True)
#quote_ctx.set_handler(OrderBookHandler())

# 报价
#quote_ctx.subscribe(code, 'QUOTE', push = True)
#quote_ctx.set_handler(StockQuoteHandler())

#逐笔
#quote_ctx.subscribe(code, 'TICKER', push = True)
#quote_ctx.set_handler(TickerHandler())

#日K
#quote_ctx.subscribe(code, 'K_DAY', push = True)
#quote_ctx.set_handler(CurKlineHandler())

#分时
#quote_ctx.subscribe(code, 'RT_DATA', push = True)
#quote_ctx.set_handler(RTDataHandler())

#经济队列
#quote_ctx.subscribe(code, 'BROKER', push = True)
#quote_ctx.set_handler(BrokerHandler())

#查看当前订阅
#ret_code, ret_data = quote_ctx.query_subscription(0)
#print ret_data

'''
低频行情
'''
#获取交易日
ret, trading_days = quote_ctx.get_trading_days(market, '2017-01-01', '2017-11-14')
print trading_days

#获取股票信息
#ret, stock_list = quote_ctx.get_stock_basicinfo(market)

#获取历史k线
#ret, history_kline = quote_ctx.get_history_kline(code, '2016-01-01', '2017-01-01', 'K_DAY', 'qfq')

#获取复权因子
#ret, autype_list = quote_ctx.get_autype_list([code])

#获取市场快照
#ret, snapshot = quote_ctx.get_market_snapshot([code])

#获取板块集合下的子版块列表
#ret, plate_list = quote_ctx.get_plate_list(market, '881166')

#获取板块下的股票列表
#ret, plate_stock = quote_ctx.get_plate_stock('SH.881166')

'''
高频行情
'''
#获取报价
#ret, stock_quote = quote_ctx.get_stock_quote([code])
#print stock_quote

#获取逐笔
#ret, rt_ticker = quote_ctx.get_rt_ticker(code, 10)
#print rt_ticker

#获取当前k线
#ret, cur_kline = quote_ctx.get_cur_kline(code, 100, 'K_DAY', 'qfq')
#print cur_kline

#获取摆盘
#ret, order_book = quote_ctx.get_order_book(code)
#print order_book

#获取分时数据
#ret, rt_data = quote_ctx.get_rt_data(code)
#print rt_data

#获取经济队列
#ret, broker_queue, _ = quote_ctx.get_broker_queue(code)
#print broker_queue

'''
#交易上下文
'''
#trader_hk_ctx = ft.OpenHKTradeContext(host = api_svr_ip, port = api_svr_port)
#trader_us_ctx = ft.OpenUSTradeContext(host = api_svr_ip, port = api_svr_port)

'''
#交易接口
'''
#解锁
#ret_code, ret_data = trader_hk_ctx.unlock_trade(password = password)

#下单
#ret_code, ret_data = trader_hk_ctx.place_order(price = 377.00, qty = 100, strcode = code, orderside = 0, ordertype = 0, envtype = trade_env)
#print ret_data

#设置订单状态
#ret_code, ret_data = trader_hk_ctx.set_order_status(status = 0, orderid = 839340, envtype = trade_env)
#print ret_data

#修改订单
#ret_code, ret_data = trader_hk_ctx.change_order(price = 366.00, qty = 100, orderid = order_id, envtype = trade_env)

#查询账户信息
#ret_code, ret_data = trader_hk_ctx.accinfo_query(trade_env)
#print ret_data

#查询订单列表
#ret_code, ret_data = trader_hk_ctx.order_list_query(statusfilter = '', envtype = trade_env)
#print ret_data

#查询持仓列表
#ret_code, ret_data = trader_hk_ctx.position_list_query(envtype = trade_env)
#print ret_data

#查询成交列表
#ret_code, ret_data = trader_hk_ctx.deal_list_query(envtype = trade_env)

time.sleep(6)
quote_ctx.stop()
