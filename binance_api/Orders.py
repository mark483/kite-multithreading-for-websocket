# -*- coding: UTF-8 -*-
# @swapnil
#import config 

from binance_api.BinanceAPI import BinanceAPI


api_key = ''
api_secret = ''
# recvWindow should less than 60000
recv_window = 5000

client = None


# You should run this func first to set up the setting for binance_api module.
def set_keys(key, secret):
    global api_key, api_secret, client
    api_key = key
    api_secret = secret

    client = BinanceAPI(api_key, api_secret, recv_window)


class Orders:
    @staticmethod
    def buy_limit(symbol, quantity, buy_price):

        order = client.buy_limit(symbol, quantity, buy_price)

        if 'msg' in order:
            print('Message : ' + order['msg'])
            return order, 'Message : ' + order['msg']

        # Buy order created.
        return order['orderId'], ''

    @staticmethod
    def sell_limit(symbol, quantity, sell_price):

        order = client.sell_limit(symbol, quantity, sell_price)  

        if 'msg' in order:
            print('Message : ' + order['msg'])
            return order, 'Message : ' + order['msg']

        return order, ''

    @staticmethod
    def buy_market(symbol, quantity):

        order = client.buy_market(symbol, quantity)  

        if 'msg' in order:
            return order, 'Message : ' + order['msg']

        return order, ''

    @staticmethod
    def sell_market(symbol, quantity):
        order = client.sell_market(symbol, quantity)

        if 'msg' in order:
            return order, 'Message : ' + order['msg']

        return order, ''

    @staticmethod
    def cancel_order(symbol, orderId):
        
        try:
            
            order = client.cancel(symbol, orderId)

            if 'msg' in order:
                print('Message : ' + order['msg'])
                return order
            
            print('Profit loss, called order, %s' % (orderId))
        
            return True
        
        except Exception as e:
            print('cancel_order Exception: %s' % e)
            return False

    @staticmethod
    def get_order_book(symbol):
        try:

            orders = client.get_order_books(symbol, 5)
            lastBid = float(orders['bids'][0][0]) #last buy price (bid)
            lastAsk = float(orders['asks'][0][0]) #last sell price (ask)
     
            return lastBid, lastAsk
    
        except Exception as e:
            print('get_order_book Exception: %s' % e)
            return 0, 0

    @staticmethod
    def get_order(symbol, orderId):
        try:

            order = client.query_order(symbol, orderId)

            if 'msg' in order:
                print('Message : ' + order['msg'])
                return False

            return order

        except Exception as e:
            print('get_order Exception: %s' % e)
            return False
    
    @staticmethod
    def get_order_status(symbol, orderId):
        try:

            order = client.query_order(symbol, orderId)

            if 'msg' in order:
                print('Message : ' + order['msg'])
                return order
        
            return order['status']
 
        except Exception as e:
            print('get_order_status Exception: %s' % e)
            return None
    
    @staticmethod
    def get_ticker(symbol):
        try:        
    
            ticker = client.get_ticker(symbol)
 
            return float(ticker['lastPrice'])
        except Exception as e:
            print('Get Ticker Exception: %s' % e)
    
    @staticmethod
    def get_info(symbol):
        try:        
    
            info = client.get_exchange_info()
            
            if symbol != "":
                return [market for market in info['symbols'] if market['symbol'] == symbol][0]
 
            return info
            
        except Exception as e:
            print('get_info Exception: %s' % e)
