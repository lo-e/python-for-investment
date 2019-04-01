# -- coding: utf-8 --

import pymongo
from vnpy.trader.app.ctaStrategy.ctaBase import TICK_DB_NAME
from vnpy.trader.app.ctaStrategy.ctaBase import DAILY_DB_NAME
from datetime import datetime
from vnpy.trader.app.ctaStrategy.stgEarningManager import stgEarningManager
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas as pd
import rqdatac as rq
from rqdatac import *
import re

userName = "license"
password = "dz9o6-SYOXqaZEoz-qUx3inb0RhitYeagYoXiwOZJjYUfHjLtQeDaopppzc1zc6K84mRGSvmlVTwOIRZ9PORzzjXhcOdlrNjD35rMZos_PtZ21RwzJWCBheJ54tvdITXDacYtBceJ1Vub7RBGmKtuQ4DCikErdOiHmpS094_0DA=HnHwvv5WoTaqyELbhBADe_6_ecoQRwWzJA6OSZmkwWPwEXHpK0ygv0nhoh_Gu07cx6QHcYvi-luA1L0pZE96B4fLIbeyTxUow-UsAt6MRZOSly89nOfhUa08bb1nE-UmcKklWn6crSXwsnxhC8vKW-FlGiM4jfIkXgWtsgZpgJA="
rq.init(userName, password)

def isFinanceSymbol(symbol):
    financeSymbols = ['IF', 'IC', 'IH']
    startSymbol = re.sub("\d", "", symbol)
    if startSymbol in financeSymbols:
        return True
    else:
        return False

if __name__ == '__main__':
    a = []
    print a
    if len(a):
        a.pop()
    print a