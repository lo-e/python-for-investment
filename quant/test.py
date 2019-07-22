# -- coding: utf-8 --
import cryptocompare

print(cryptocompare.get_historical_price_day_with_exchange('EOS', curr='USDT', exchange='OKEX'))

if __name__ == '__main__':
    pass


