# -*- coding: utf-8 -*-

import futuquant as ft

#实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host = '127.0.0.1', port = 11111)
print 'abc'

#上下文控制
quote_ctx.start()
quote_ctx.stop()
quote_ctx.set_handler('')

#低频数据接口
trading_days = quote_ctx.get_trading_days('HK', '1970-01-01', '2017-01-01')
stock_list = quote_ctx.get_stock_basicinfo('HK')
history_kline = quote_ctx.get_history_kline('HK.00060', '2016-01-01', '2017-01-01', 'K_DAY', 'qfq')