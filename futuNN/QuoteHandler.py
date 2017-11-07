# -*- coding: utf-8 -*-

from futuquant.open_context import *

'''
报价
'''
class StockQuoteHandler(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(StockQuoteHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print u'报价'
            print 'StockQuoteHandler error: %s' % content
            return RET_ERROR, content
        else:
            print u'======报价======'
            print '======StockQuoteHandler====== \n', content
            return RET_OK, content

'''
摆盘
'''
class OrderBookHandler(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(OrderBookHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print u'摆盘'
            print 'OrderBookHandler error: %s' % content
            return RET_ERROR, content
        else:
            print u'======摆盘======'
            print '======OrderBookHandler====== \n', content
            return RET_OK, content

'''
实时k线
'''
class CurKlineHandler(CurKlineHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(CurKlineHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print u'实时k线'
            print 'CurKlineHandler error: %s' % content
            return RET_ERROR, content
        else:
            print u'======实时k线======'
            print '======CurKlineHandler====== \n', content
            return RET_OK, content

'''
逐笔
'''
class TickerHandler(TickerHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(TickerHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print u'逐笔'
            print 'TickerHandler error: %s' % content
            return RET_ERROR, content
        else:
            print u'======逐笔======'
            print '======TickerHandler====== \n', content
            return RET_OK, content

'''
分时
'''
class RTDataHandler(RTDataHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(RTDataHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print u'分时'
            print 'RTDataHandler error: %s' % content
            return RET_ERROR, content
        else:
            print u'======分时======'
            print '======RTDataHandler====== \n', content
            return RET_OK, content

'''
经纪队列
'''
class BrokerHandler(BrokerHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(BrokerHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print u'经纪队列'
            print 'BrokerHandler error: %s' % content
            return RET_ERROR, content
        else:
            print u'======经纪队列======'
            print '======BrokerHandler====== \n', content
            return RET_OK, content

#===============================================
if __name__ == '__main__':
    print 'OrderBookHandler main!!'
