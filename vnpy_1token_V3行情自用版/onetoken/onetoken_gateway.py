# encoding: UTF-8
import hashlib
import sys
import hmac
import json
import shelve
from time import time
from datetime import datetime,timedelta
import pandas as pd
from threading import Lock
from urllib.parse import urlparse
from copy import copy,deepcopy
import os
import csv
from requests import ConnectionError
from peewee import chunked
from vnpy.trader.object import BarData
from vnpy.trader.constant import (Exchange, Interval)
from vnpy.trader.database import database_manager
from vnpy.api.rest import Request, RestClient
from vnpy.api.websocket import WebsocketClient
from vnpy.trader.constant import (Direction, Exchange, Status, Offset, Product)
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (TickData, PositionData, AccountData,
                                OrderRequest, CancelRequest, SubscribeRequest,
                                ContractData, OrderData, TradeData)
from vnpy.trader.event import EVENT_TIMER
from vnpy.trader.setting import luncer_account  #导入账户字典
from vnpy.app.cta_strategy.usual_method import CheckFutureNews
from vnpy.trader.utility import get_folder_path,load_json, save_json,utc_to_local
recording_list = CheckFutureNews().recording_list
recording_list = [X for X in recording_list if "BITMEX" in X]
#交易host
TRADING_HOST = ["1token.trade/api","api.1token.trade","cdn.1tokentrade.cn/api"][2]
REST_HOST = f"https://{TRADING_HOST}"
DATA_WEBSOCKET_HOST = f"wss://{TRADING_HOST}/v1/ws/tick-v3"  
TRADE_WEBSOCKET_HOST = f"wss://{TRADING_HOST}/v1/ws/trade"

DIRECTION_VT2ONETOKEN = {Direction.LONG: "b", Direction.SHORT: "s"}
DIRECTION_ONETOKEN2VT = {v: k for k, v in DIRECTION_VT2ONETOKEN.items()}

EXCHANGE_VT2ONETOKEN = {Exchange.BITFINEX: "bitfinex",Exchange.BITHUMB: "bithumb",Exchange.BINANCE: "binance",Exchange.OKEX: "okex", Exchange.OKEF: "okef", Exchange.HUOBIP: "huobip", Exchange.HUOBIM: "huobim", Exchange.HUOBIF: "huobif", Exchange.BITMEX: "bitmex"}
EXCHANGE_ONETOKEN2VT = {v: k for k, v in EXCHANGE_VT2ONETOKEN.items()}
EXCHANGE_CHOOSE = -1 #交易所选择,bitmex
#-------------------------------------------------------------------------------------------------
class OnetokenGateway(BaseGateway):
    """
    VN Trader Gateway for 1Token connection
    """

    default_setting = {
        "OT Key": "",
        "OT Secret": "",
        "交易所": ["BINANCE", "BITMEX","BITFINEX","BITHUMB","OKEX", "OKEF","OKSWAP", "HUOBIP", "HUOBIM", "HUOBIF"],
        "账户": "",
        "会话数": 3,
        "代理地址": "127.0.0.1",
        "代理端口": 1080,
    }

    exchanges = list(EXCHANGE_VT2ONETOKEN.keys())
    #-------------------------------------------------------------------------------------------------
    def __init__(self, event_engine):
        """Constructor"""
        super(OnetokenGateway, self).__init__(event_engine, "1TOKEN")

        self.rest_api = OnetokenRestApi(self)
        self.data_ws_api = OnetokenDataWebsocketApi(self)
        self.trade_ws_api = OnetokenTradeWebsocketApi(self)

        self.count = 0          #心跳计数
        self.cancel_count = 0   #撤单计数
    #-------------------------------------------------------------------------------------------------    
    def connect(self):
        """"""
        key = luncer_account["OT Key"]
        secret = luncer_account["OT Secret"]
        session_number = luncer_account["会话数"]
        exchange = list(EXCHANGE_VT2ONETOKEN.values())[EXCHANGE_CHOOSE]   #bitmex
        account = luncer_account["账户"]
        proxy_host = luncer_account["代理地址"]
        proxy_port = luncer_account["代理端口"]

        self.rest_api.connect(key, secret, session_number, exchange, account,
                              proxy_host, proxy_port)
        self.data_ws_api.connect(proxy_host, proxy_port)
        self.trade_ws_api.connect(key, secret, exchange, account, proxy_host,
                                  proxy_port)
        self.init_ping()
    #-------------------------------------------------------------------------------------------------   
    def subscribe(self, req: SubscribeRequest):
        """"""
        self.data_ws_api.subscribe(req)
    #-------------------------------------------------------------------------------------------------   
    def send_order(self, req: OrderRequest):
        """"""
        return self.rest_api.send_order(req)
    #-------------------------------------------------------------------------------------------------   
    def cancel_order(self, req: CancelRequest):
        """"""
        self.rest_api.cancel_order(req)
    #-------------------------------------------------------------------------------------------------   
    def query_account(self):
        """"""
        pass
    #-------------------------------------------------------------------------------------------------   
    def query_position(self):
        """"""
        pass
    #-------------------------------------------------------------------------------------------------   
    def query_candle(self, event):
        """写入当日分钟数据"""   
        all_contracts = recording_list
        if len(all_contracts) > 0:
            symobl,exchange = all_contracts[0].split("_")
            self.rest_api.query_candle(symobl)
            all_contracts.pop(0)
    #-------------------------------------------------------------------------------------------------   
    def cancel_all_orders(self, event):
        """半小时轮询撤销所有未成交委托单"""
        self.cancel_count += 1
        if self.cancel_count < 1800:
            return
        self.cancel_count = 0
        cancel_contracts = recording_list
        for contract in cancel_contracts:
            symobl,exchange = contract.split("_")
            self.rest_api.cancel_all_orders(symobl)
    #-------------------------------------------------------------------------------------------------   
    def close(self):
        """"""
        self.rest_api.stop()
        self.data_ws_api.stop()
        self.trade_ws_api.stop()
    #-------------------------------------------------------------------------------------------------   
    def process_timer_event(self, event):
        """"""
        self.count += 1
        if self.count < 20:
            return
        self.count = 0

        self.data_ws_api.ping()
        self.trade_ws_api.ping()
    #-------------------------------------------------------------------------------------------------   
    def init_ping(self):
        """"""
        self.event_engine.register(EVENT_TIMER, self.process_timer_event)
        self.event_engine.register(EVENT_TIMER, self.rest_api.process_over_load)
        self.event_engine.register(EVENT_TIMER, self.query_candle)
        self.event_engine.register(EVENT_TIMER, self.cancel_all_orders)

#-------------------------------------------------------------------------------------------------   
class OnetokenRestApi(RestClient):
    """
    1Token REST API
    """

    def __init__(self, gateway: BaseGateway):
        """"""
        super(OnetokenRestApi, self).__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name
        self.key = ""
        self.secret = ""
        self.exchange = ""
        self.over_load_list = []         #过载标的
        self.request_file_name = 'request_data'
        self.request_file_path = get_folder_path(self.request_file_name)        #委托类存储路径
        self.order_count = 1_000_000
        self.order_count_lock = Lock()
        self.one_token_order_id = ""
        self.connect_time = 0
        self.account = ""
        self.all_contracts = []         #所有vt_symbol合约列表
        self.sen_order_data = {}        #发送委托单字典
        self.over_load_count = 0        #过载处理计数
    #-------------------------------------------------------------------------------------------------   
    def sign(self, request):
        """
        Generate 1Token signature.
        """
        method = request.method

        endpoint = "/" + request.path.split("/", 3)[3]
        parsed_url = urlparse(endpoint)
        path = parsed_url.path

        nonce = str(int(time() * 1e6))
        data = request.data
        json_str = data if data else ""

        message = method + path + nonce + json_str

        signature = hmac.new(bytes(self.secret, "utf8"), bytes(message, "utf8"), digestmod=hashlib.sha256).hexdigest()

        headers = {
            "Api-Nonce": nonce,
            "Api-Key": self.key,
            "Api-Signature": signature,
            "Content-Type": "application/json"
        }
        request.headers = headers

        return request
    #-------------------------------------------------------------------------------------------------   
    def connect(self, key: str, secret: str, session_number: int, exchange: str, account: str, proxy_host: str, proxy_port: int, ):
        """
        Initialize connection to REST server.
        """
        self.key = key
        self.secret = secret
        self.exchange = exchange
        self.account = account
        self.connect_time = (int(datetime.now().strftime("%y%m%d%H%M%S")) * self.order_count)

        self.init(REST_HOST, proxy_host, proxy_port)

        self.start(session_number)

        self.gateway.write_log("REST API启动成功")

        self.query_time()
        self.query_contract()
        self.query_currency_rate()
    #-------------------------------------------------------------------------------------------------   
    def _new_order_id(self):
        with self.order_count_lock:
            self.order_count += 1
            return self.order_count
    #-------------------------------------------------------------------------------------------------   
    def query_time(self):
        """"""
        self.add_request("GET", "/v1/basic/time", callback=self.on_query_time)
    #-------------------------------------------------------------------------------------------------   
    def on_query_time(self, data, request):
        """查询服务器时间"""
        server_timestamp = data["server_time"]
        dt = datetime.utcfromtimestamp(server_timestamp)
        server_time = dt.isoformat() + "Z"
        local_time = datetime.utcnow().isoformat()
        msg = f"服务器时间：{server_time}，本机时间：{local_time}"
        self.gateway.write_log(msg)
    #-------------------------------------------------------------------------------------------------   
    def query_currency_rate(self):
        """查询当前汇率"""
        self.add_request("GET", "/v1/basic/currency-rate", callback=self.on_currency_rate)
    #-------------------------------------------------------------------------------------------------   
    def on_currency_rate(self,data, request):
        self.gateway.write_log(f"美元兑人民币：{round(data['usd.cny'],3)},btc市值:{round(data['btc.cny'],3)},eth市值:{round(data['eth.cny'],3)}")
    #------------------------------------------------------------------------------------------------- 
    def query_candle(self,symbol):
        """查询分钟数据"""
        self.add_request("GET", f"/v1/quote/candles?contract={self.exchange}/{symbol}&duration=1m&since=now-1d", callback=self.on_candle)
    #------------------------------------------------------------------------------------------------- 
    def cancel_all_orders(self,symbol):
        """撤销合约所有未成交订单"""
        params = {'contract':self.exchange + "/" + symbol}
        self.add_request(
            method="DELETE",
            path="/v1/trade/{}/{}/orders/all".format(self.exchange, self.account),
            callback=self.on_cancel_all,
            params=params,
            on_error=self.on_cancel_all_error)         
    #------------------------------------------------------------------------------------------------- 
    def on_candle(self,data, request):
        """当天分钟数据写入数据库"""
        bars = []
        start_time = None
        count = 0
        time_consuming_start = time()
        for candle in data:
            bar = BarData(
                symbol=candle['contract'].split('/')[1],
                exchange=Exchange(candle['contract'].split('/')[0].upper()),
                datetime = datetime.fromtimestamp(candle['timestamp']),
                interval=Interval.MINUTE,
                open_price=candle['open'],
                high_price=candle['high'],
                low_price=candle['low'],
                close_price=candle['close'],
                volume=candle['volume'],
                gateway_name = 'DB'
                )           
            if not start_time:
                start_time = bar.datetime
            bars.append(bar)
            count += 1
        if not bars:
            return
        end_time = bar.datetime  
        for X in chunked(bars, 10000):               #分批保存数据
            database_manager.save_bar_data(X,True)      #保存数据到数据库  
        time_consuming_end =time()
        print(f'载入{bar.vt_symbol}:bar数据，开始时间：{start_time}，结束时间：{end_time}，数据量：{count},耗时：{round(time_consuming_end-time_consuming_start,3)}秒')
    #-------------------------------------------------------------------------------------------------   
    def query_contract(self):
        """查询合约"""
        self.add_request("GET", "/v1/basic/contracts?exchange={}".format(self.exchange), callback=self.on_query_contract)
    #-------------------------------------------------------------------------------------------------   
    def on_query_contract(self, data, request):
        """"""
        for instrument_data in data:
            symbol = instrument_data["name"]                        #合约名称,格式btc.usdt
            contract = ContractData(
                symbol=symbol,              
                exchange=Exchange(instrument_data['symbol'].split('/')[0].upper()), 
                name=symbol,
                min_volume=float(instrument_data["min_amount"]),           #合约最小成交量变动
                price_tick=float(instrument_data["min_change"]),           #合约最小价格变动   
                gateway_name=self.gateway_name)
            if contract.exchange.value in ("OKEF","BITMEX","OKSWAP","HUOBIF"):
                contract.product = Product.FUTURES
            else:
                contract.product = Product.SPOT
            if instrument_data["max_leverage"]:
                contract.size = float(instrument_data["max_leverage"])      #合约最大杠杆
            if f"{contract.symbol}_{contract.exchange.value}" not in self.all_contracts:
                self.all_contracts.append(f"{contract.symbol}_{contract.exchange.value}")
            self.gateway.on_contract(contract)
            self.gateway.on_all_contracts(self.all_contracts)
        self.gateway.write_log("合约信息查询成功")

        #合约信息查询完毕启动行情api，交易api
        self.gateway.data_ws_api.start()
        self.gateway.trade_ws_api.start()
    #-------------------------------------------------------------------------------------------------   
    def send_order(self, req: OrderRequest):
        """"""
        self.one_token_order_id = self.exchange + "/" + req.symbol + "-" + str(self.connect_time + self._new_order_id())
        #保存委托类到本地
        request_save = shelve.open(f"{self.request_file_path}\\request_data.vt")
        request_save[req.vt_symbol] = req
        request_save.close()
        data = {
            "contract": self.exchange + "/" + req.symbol,
            "price": float(req.price),
            "bs": DIRECTION_VT2ONETOKEN[req.direction],
            "amount": float(req.volume),
            "client_oid": self.one_token_order_id
        }

        if req.offset == Offset.CLOSE:
            data["options"] = {"close": True}
        data = json.dumps(data)
        order = req.create_order_data(self.one_token_order_id, self.gateway_name)

        self.add_request(
            method="POST",
            path="/v1/trade/{}/{}/orders".format(self.exchange, self.account),
            callback=self.on_send_order,
            data=data,
            params={},
            extra=order,
            on_failed=self.on_send_order_failed,
            on_error=self.on_send_order_error)

        self.gateway.on_order(order)
        return order.vt_orderid
    #-------------------------------------------------------------------------------------------------   
    def cancel_order(self, req: CancelRequest):
        """"""
        #1token撤单需要使用exchange_oid
        #撤单的orderid与报单的client_oid相同，使用报单的exchange_oid撤单
        if req.orderid in self.sen_order_data:
            exchange_oid = self.sen_order_data[req.orderid]["exchange_oid"]
            params = {"exchange_oid": exchange_oid}
            self.add_request(
                method="DELETE",
                path="/v1/trade/{}/{}/orders".format(self.exchange, self.account),
                callback=self.on_cancel_order,
                params=params,
                on_error=self.on_cancel_order_error,
                extra=req)
        #如果撤单委托ID不在委托ID映射字典里面，撤销标的全部未成交订单
        else:
            params = {'contract':self.exchange + "/" + req.symbol}
            self.add_request(
                method="DELETE",
                path="/v1/trade/{}/{}/orders/all".format(self.exchange, self.account),
                callback=self.on_cancel_all,
                params=params,
                on_error=self.on_cancel_all_error,
                extra=req)      
    #-------------------------------------------------------------------------------------------------   
    def on_send_order(self, data, request):
        """收到发单推送"""
        self.sen_order_data = load_json("one_token_order_map.json")
        self.sen_order_data[data["client_oid"]] = data
        #缓存最新100个委托ID映射
        if len(self.sen_order_data) > 100:
            del self.sen_order_data[list(self.sen_order_data.keys())[0]]
        save_json("one_token_order_map.json",self.sen_order_data)
    #-------------------------------------------------------------------------------------------------   
    def on_send_order_failed(self, status_code: str, request: Request):
        """
        收到发单失败回调
        """
        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)
        error_code = request.response.json()
        if error_code["code"] == "exg-system-overloaded":         #过载回报代码
            if order.vt_symbol not in self.over_load_list:
                self.over_load_list.append(order.vt_symbol)
        msg = f"委托失败，状态码：{status_code}，信息：{request.response.text}"
        self.gateway.write_log(msg)
    #-------------------------------------------------------------------------------------------------   
    def process_over_load(self, event): 
        """BITMEX过载处理"""
        self.over_load_count += 1
        if self.over_load_count < 2:
            return
        self.over_load_count = 0
        for vt_symbol in self.over_load_list:
            request_load = shelve.open(f"{self.request_file_path}\\request_data.vt")
            if vt_symbol in request_load:
                request_data = request_load[vt_symbol]

                self.send_order(request_data)
                msg = f"过载重新下单,交易标的:{request_data.vt_symbol},方向:{request_data.direction.value},价格:{request_data.price},发单量:{request_data.volume}"
                self.gateway.write_log(msg)  
            request_load.close()                            
            self.over_load_list.remove(vt_symbol)

    #-------------------------------------------------------------------------------------------------   
    def on_send_order_error(self, exception_type: type,
                            exception_value: Exception, tb, request: Request):
        """
        Callback when sending order caused exception.
        """
        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)

        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)
    #-------------------------------------------------------------------------------------------------   
    def on_cancel_order(self, data, request):
        """Websocket will push a new order status"""
        pass
    #-------------------------------------------------------------------------------------------------   
    def on_cancel_order_error(self, exception_type: type,
                              exception_value: Exception, tb, request: Request):
        """
        Callback when cancelling order failed on server.
        """
        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)
    #-------------------------------------------------------------------------------------------------  
    def on_cancel_all(self, data, request):   
        #收到撤销全部未成交订单回报 
        pass
    #-------------------------------------------------------------------------------------------------  
    def on_cancel_all_error(self, exception_type: type, exception_value: Exception, tb, request: Request):
        #撤销全部未成交订单错误回报
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)  
#-------------------------------------------------------------------------------------------------   
class OnetokenDataWebsocketApi(WebsocketClient):
    """"""

    def __init__(self, gateway):
        """"""
        super().__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

        self.ticks = {}
        self.data_connect_status = False        #行情连接状态
        self.callbacks = {
            "auth": self.on_login,
            "single-tick-verbose": self.on_tick
        }    
        save_json("onetoken_data_status.json",True)     #设置onetoken_data_status默认为True
        self.data_status_count = 0      #行情登录记数
        self.order_book_bids = {}       #订单簿买单字典
        self.order_book_asks = {}       #订单簿卖单字典
    #-------------------------------------------------------------------------------------------------   
    def connect(self, proxy_host: str, proxy_port: int):
        """"""
        self.init(DATA_WEBSOCKET_HOST, proxy_host, proxy_port)
    #-------------------------------------------------------------------------------------------------   
    def subscribe(self, req: SubscribeRequest):
        """
        订阅tick行情
        """
        tick = TickData(
            symbol=req.symbol,
            exchange=req.exchange,
            name=req.symbol,
            datetime=datetime.now(),
            gateway_name=self.gateway_name,
        )
        contract_symbol = f"{req.exchange.value.lower()}/{req.symbol.lower()}"
        self.ticks[contract_symbol] = tick

        req = {
            "uri": "subscribe-single-tick-verbose",
            "contract": contract_symbol
        }
        self.send_packet(req)
    #-------------------------------------------------------------------------------------------------   
    def on_connected(self):
        """"""
        if not self.data_connect_status:
            self.gateway.write_log("行情Websocket API连接成功")
            self.login()
            self.data_connect_status = True
    #-------------------------------------------------------------------------------------------------   
    def on_disconnected(self):
        """"""
        self.data_connect_status = False
        self.gateway.write_log("行情Websocket API连接断开")
    #-------------------------------------------------------------------------------------------------   
    def on_packet(self, packet: dict):
        """"""
        channel = packet.get("uri", "")
        data = packet.get("data", None)
        callback = self.callbacks.get(channel, None)
        if callback:
            callback(data)   
        else:
            tick_type = packet.get("tp",None)
            if tick_type:                #推送V3行情
                self.on_tick_v3(packet)
    #-------------------------------------------------------------------------------------------------   
    def on_error(self, exception_type: type, exception_value: Exception, tb):
        """"""
        self.gateway.write_log(self.exception_detail(exception_type, exception_value, tb))
    #-------------------------------------------------------------------------------------------------   
    def login(self):
        """
        Need to login befores subscribe to websocket topic.
        """
        req = {"uri": "auth"}
        self.send_packet(req)

    #-------------------------------------------------------------------------------------------------   
    def on_login(self, data: dict):
        """"""
        self.gateway.write_log("行情Websocket API登录成功")
        #登录两次行情1token行情会堵塞，行情状态设置为False，由交易进程重启
        self.data_status_count += 1
        if self.data_status_count >= 2:
            save_json("onetoken_data_status.json",False)
    #-------------------------------------------------------------------------------------------------   
    def on_tick(self, data: dict):
        """收到L1 tick行情"""
        contract_symbol = data["contract"]
        tick = self.ticks.get(contract_symbol, None)
        if not tick:
            return
        tick.last_price = data["last"]
        tick.datetime = datetime.strptime(data["time"][:-6],
                                          "%Y-%m-%dT%H:%M:%S.%f")
        bids = data["bids"]
        asks = data["asks"]
        for n, buf in enumerate(bids):
            tick.__setattr__("bid_price_%s" % (n + 1), buf["price"])
            tick.__setattr__("bid_volume_%s" % (n + 1), buf["volume"])

        for n, buf in enumerate(asks):
            tick.__setattr__("ask_price_%s" % (n + 1), buf["price"])
            tick.__setattr__("ask_volume_%s" % (n + 1), buf["volume"])
        self.gateway.on_tick(copy(tick))
    #-------------------------------------------------------------------------------------------------   
    def on_tick_v3(self,packet:dict):
        """
        收到v3行情推送
        """
        contract_symbol = packet["c"]       #合约代码
        new_tick = self.ticks.get(contract_symbol,None)
        if not new_tick:
            return
        new_tick.last_price =  packet["l"]     #tick最新价
        new_tick.datetime = pd.to_datetime(packet["tm"], unit = "s")   + timedelta(hours=8)         #tick时间
        new_tick.volume = packet["v"]       #v,tick成交量，vu换算成USD的成交量，vc换算成人民币的成交量
        if packet.get("tp",None) == "s":         #收到快照行情
            self.order_book_bids[new_tick.vt_symbol] = {}
            self.order_book_asks[new_tick.vt_symbol] = {}
        bids,asks = packet["b"][:5],packet["a"][:5]           #tick买卖单信息 
        for bid_data in bids:
            self.order_book_bids[new_tick.vt_symbol].update({str(bid_data[0]):bid_data[1]})
            #order_book_bids删除委托量为0的价格缓存
            if not bid_data[1]:
                del self.order_book_bids[new_tick.vt_symbol][str(bid_data[0])]
        for ask_data in asks:
            self.order_book_asks[new_tick.vt_symbol].update({str(ask_data[0]):ask_data[1]})   
            if not ask_data[1]:
                del self.order_book_asks[new_tick.vt_symbol][str(ask_data[0])]
        sort_bids = sorted(self.order_book_bids[new_tick.vt_symbol].items(), key=lambda x:float(x[0]),reverse=True)    #买单从高到低排序
        sort_asks = sorted(self.order_book_asks[new_tick.vt_symbol].items(), key=lambda x:float(x[0]),reverse=False)   #卖单从低到高排序
        for n,buf in enumerate(sort_bids):
            new_tick.__setattr__(f"bid_price_{(n + 1)}", float(buf[0]))
            new_tick.__setattr__(f"bid_volume_{(n + 1)}", buf[1])
        for n,buf in enumerate(sort_asks):
            new_tick.__setattr__(f"ask_price_{(n + 1)}" , float(buf[0]))
            new_tick.__setattr__(f"ask_volume_{(n + 1)}", buf[1])
        self.gateway.on_tick(copy(new_tick))        
    #-------------------------------------------------------------------------------------------------   
    def ping(self):
        """"""
        self.send_packet({"uri": "ping"})
#-------------------------------------------------------------------------------------------------   
class OnetokenTradeWebsocketApi(WebsocketClient):
    """"""

    def __init__(self, gateway):
        """"""
        super().__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

        self.key = ""
        self.secret = ""
        self.exchange = ""
        self.account = ""

        self.trade_count = 0
        self.trade_connect_status = False
        self.callbacks = {
            "sub-info": self.on_subscribe_info,
            "sub-order": self.on_subscribe_order,
            "info": self.on_info,
            "order": self.on_order
        }
        self.positions = {}         #持仓字典
    #-------------------------------------------------------------------------------------------------   
    def connect(self, key: str, secret: str, exchange: str, account: str,
                proxy_host: str, proxy_port: int):
        """"""
        self.key = key
        self.secret = secret
        self.exchange = exchange
        self.account = account

        # Create header for ws connection
        nonce = str(int(time() * 1e6))
        path = f"/ws/{self.account}"
        message = "GET" + path + nonce

        signature = hmac.new(bytes(self.secret, "utf8"), bytes(message, "utf8"), digestmod=hashlib.sha256).hexdigest()

        header = {
            "Api-Nonce": nonce,
            "Api-Key": self.key,
            "Api-Signature": signature
        }
        host = f"{TRADE_WEBSOCKET_HOST}/{self.exchange}/{self.account}"

        self.init(host, proxy_host, proxy_port, header=header)
    #-------------------------------------------------------------------------------------------------   
    def subscribe_info(self):
        """
        Subscribe to account update.
        """
        self.send_packet({"uri": "sub-info"})
    #-------------------------------------------------------------------------------------------------   
    def subscribe_order(self):
        """
        Subscribe to order update.
        """
        self.send_packet({"uri": "sub-order"})
    #-------------------------------------------------------------------------------------------------   
    def on_connected(self):
        """"""
        if not self.trade_connect_status:
            self.gateway.write_log("交易Websocket API连接成功")
            self.subscribe_info()
            self.subscribe_order()
            self.trade_connect_status = True
    #-------------------------------------------------------------------------------------------------   
    def on_disconnected(self):
        """"""
        self.gateway.write_log("交易Websocket API连接断开")
        self.trade_connect_status = False
    #-------------------------------------------------------------------------------------------------   
    def on_packet(self, packet: dict):
        """"""
        # Reply
        if "uri" in packet:
            channel = packet["uri"]

            if "data" in packet:
                data = packet["data"]
            elif "code" in packet:
                data = packet["code"]
            else:
                data = None
        # Push
        elif "action" in packet:
            channel = packet["action"]
            data = packet.get("data", None) 
        callback = self.callbacks.get(channel, None)
        if callback:
            callback(data)
    #-------------------------------------------------------------------------------------------------   
    def on_error(self, exception_type: type, exception_value: Exception, tb):
        """"""
        self.gateway.write_log(self.exception_detail(exception_type, exception_value, tb))
    #-------------------------------------------------------------------------------------------------   
    def on_subscribe_info(self, data: str):
        """"""
        if data == "success":
            self.gateway.write_log("账户资金推送订阅成功")
    #-------------------------------------------------------------------------------------------------   
    def on_subscribe_order(self, data: str):
        """"""
        if data == "success":
            self.gateway.write_log("委托更新推送订阅成功")
    #-------------------------------------------------------------------------------------------------   
    def on_info(self, data: dict):
        """"""
        #收到账户回报
        position_detail = data.get('position',None)
        if not position_detail:
            return
        for position_data in position_detail:
            account_type = position_data["type"]
            #position_detail[0]  future-spot字典
            if account_type == "future":   
                local_time = utc_to_local(position_data["detail"]["currentTimestamp"])
                current_date,current_time = local_time.date(),local_time.time()
                account = AccountData(
                    accountid=position_data["detail"]["account"],            #账户ID
                    date = str(current_date),
                    time = str(current_time),
                    pre_balance=round(data["balance"],3),                      #人民币计价总资金
                    balance = round(position_detail[0]["total_amount"],3),           #btc计价总资金
                    available=round(position_detail[0]["available"],3),                     #btc计价可用资金
                    commission = round(position_data['detail']["commission"],4),
                    frozen=position_data['frozen'],
                    close_profit =position_data["detail"]["realisedGrossPnl"]/1e8,          #总平仓盈亏
                    position_profit =position_data["detail"]["unrealisedGrossPnl"]/1e8,     #总持仓盈亏
                    gateway_name=self.gateway_name) 
                account.margin = round(account.balance - account.available,3)                    #btc计价占用保证金
                try:
                    account.percent=round(account.margin / account.balance,3) * 100      #资金使用率
                except:
                    account.percent = 0
                self.gateway.on_account(account)
                account_info = account.__dict__
                #保存账户资金信息
                one_token_account_path = CheckFutureNews().ctp_account_path.replace("ctp_account","one_token_account")
                if not os.path.exists(one_token_account_path): # 如果文件不存在，需要写header
                    with open(one_token_account_path, 'w',newline="") as f1:#newline=""不自动换行
                        w1 = csv.DictWriter(f1, account_info.keys())
                        w1.writeheader()
                        w1.writerow(account_info)
                        f1.close()
                else: # 文件存在，不需要写header
                    with open(one_token_account_path,'a',newline="") as f1:  #a二进制追加形式写入
                        if datetime.now().hour % 8 == 0 and datetime.now().minute == 0 and datetime.now().second % 20 == 0:#8小时20秒记录一次
                            w1 = csv.DictWriter(f1, account_info.keys())
                            w1.writerow(account_info)
                            f1.close()
                #多空持仓必须同时获取，防止仓位出错
                long_position = PositionData(
                    symbol=position_data["contract"],
                    exchange=Exchange(self.exchange.upper()),  
                    direction=Direction.LONG,
                    price=position_data["average_open_price_long"],
                    volume=position_data["total_amount_long"],
                    pnl=position_data["unrealized_long"],
                    frozen=position_data["frozen_position_long"],
                    gateway_name=self.gateway_name,
                )
                short_position = PositionData(
                    symbol=position_data["contract"],
                    exchange=Exchange(self.exchange.upper()), 
                    direction=Direction.SHORT,
                    price=position_data["average_open_price_short"],
                    volume=position_data["total_amount_short"],
                    pnl=position_data["unrealized_short"],
                    frozen=position_data["frozen_position_short"],
                    gateway_name=self.gateway_name,
                )
                self.positions[f"{long_position.symbol}_{long_position.direction}"] = long_position
                self.positions[f"{short_position.symbol}_{short_position.direction}"] = short_position
                
        for position in list(self.positions.values()):
            self.gateway.on_position(position)
        self.positions.clear()
    #-------------------------------------------------------------------------------------------------   
    def on_order(self, data: dict):
        """"""
        #收到委托回报
        #未收到数据直接返回
        if not data:
            return         
        for order_data in data:
            contract_symbol = order_data["contract"]
            exchange_str, symbol = contract_symbol.split("/")
            order_date,order_time =order_data["entrust_time"].split('T')
            orderid = order_data["client_oid"]
            order = OrderData(
                symbol=symbol,
                exchange=EXCHANGE_ONETOKEN2VT[exchange_str],
                orderid=orderid,
                direction=DIRECTION_ONETOKEN2VT[order_data["bs"]],
                price=order_data["entrust_price"],
                volume=order_data["entrust_amount"],
                traded=order_data["dealt_amount"],
                date = order_date,
                time=order_time[:-6],
                cancel_time = order_data["canceled_time"],
                gateway_name=self.gateway_name)
            if order_data["tags"].get("type","") == "close":
                order.offset = Offset.CLOSE
            #撤单状态，撤单，部分撤单
            if order_data["status"] in ("withdrawn","part-deal-withdrawn"):
                order.status = Status.CANCELLED
            else:
                if order.traded == order.volume:
                    order.status = Status.ALLTRADED
                elif not order.traded:
                    order.status = Status.NOTTRADED
                else:
                    order.status = Status.PARTTRADED

            self.gateway.on_order(order)

            #推送交易数据
            if order_data["dealt_amount"]:
                trade_date,trade_time =order_data["entrust_time"].split('T')
                self.trade_count += 1
                trade = TradeData(
                    symbol=order.symbol,
                    exchange=order.exchange,
                    orderid=orderid,
                    tradeid=str(self.trade_count),
                    direction=order.direction,
                    offset = order.offset,
                    price=order_data["average_dealt_price"],
                    volume=order_data["dealt_amount"],
                    gateway_name=self.gateway_name,
                    date=trade_date,
                    time=trade_time[:-6])
                self.gateway.on_trade(trade)
    #-------------------------------------------------------------------------------------------------   
    def ping(self):
        """"""
        self.send_packet({"uri": "ping"})
    #-------------------------------------------------------------------------------------------------   