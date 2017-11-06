# -*- coding: utf-8 -*-

import futuquant as ft
import time
import datetime

#服务器ip
api_svr_ip = '119.29.141.202'
#api_svr_ip = '127.0.0.1'

#服务器端口
api_svr_port = 11111

#交易密码
password = 123456

#股票代码
code = 'HK.00700'

#股票市场
market = 'HK'

#交易环境，实盘交易：0 模拟环境：1（美股不支持模拟）
trade_env = 1

'''
行情上下文
'''
#实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host = api_svr_ip, port = api_svr_port)

#订阅高频数据查询
#quote_ctx.subscribe(code, 'ORDER_BOOK', push = False) #摆盘
#quote_ctx.subscribe(code, 'QUOTE', push = False) #报价
#quote_ctx.subscribe(code, 'TICKER', push = False) #逐笔
#quote_ctx.subscribe(code, 'K_DAY', push = False) #日K
#quote_ctx.subscribe(code, 'RT_DATA', push = False) #分时
quote_ctx.subscribe(code, 'BROKER', push = False) #经济队列

#查看当前订阅
ret_code, ret_data = quote_ctx.query_subscription(0)
print ret_data

'''
#上下文控制
'''
#开启异步数据接收
quote_ctx.start()

#停止异步数据接受
quote_ctx.stop()

#设置用于异步处理数据的回调对象
quote_ctx.set_handler('')

'''
#低频数据接口
'''
#获取交易日
#ret, trading_days = quote_ctx.get_trading_days(market=market, '1970-01-02', '2017-01-01')

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
#高频数据接口
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
#实例化港股交易上下文对象
'''
#trader_hk_ctx = ft.OpenHKTradeContext(host = api_svr_ip, port = api_svr_port)

'''
#实例化美股交易上下文对象
'''
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
