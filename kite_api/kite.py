"""
##This file is with modification where you added line 233-294 for the orders to be executed when you have action == 'do nothing'
action = action from neural net
action_1 = action of kite.py
action_2 = action from orders_q
action_stag = results action from stagnation params 
action_stag_1 = results action from def stag() function
#12345 serach for the lines where the mods happened
#123456:
1. self.quantity > self.min_quantity
2. actiona_queue.append moved it to profits function from orders_q
3. Moved self.quantity += units and -= units to the profits function
#789
1. Muted the 'buy' and 'sell' in actions_queue[-4:]
2. Addded the units = abs (self.quantity) - self.buffer_quantity
"""

import logging
import statistics
from datetime import datetime
from kiteconnect import KiteConnect
from kite_api.kite_modes import CNCMode, GTTMode, MISMode
#Function 2 -- Where you define investment() in scenarios where the you buyied and havent sell and you want to know whether you are profitable or not ?
import statistics as s



##import rocp variable 
#import sys
#sys.path.append(".")
#from corrector import Corrector
#corrector = Corrector ("ROCP", "60", "MIS")
#cost_factor_1, cost_factor_2, rocp, pull = corrector._rocp()
#print(rocp)

##Replaced units with units and units
units_factor = 1
#units = 1*units_factor 
#units = 1*units_factor
#units = 1*units_factor


max_total_sell = 50

STAG = {
    "MIS":1
    ,
    "CNC":1
}

LT_2 = {
    "MIS":0
    ,
    "CNC":0 
}


PULL = {
    "MIS":0
    ,
    "CNC":0 
}

COST_FACTORS = {
    "MIS": {
        "BUY": 0.00125,
        "SELL": 0.00125,
    },
    "CNC": {
        "BUY": 0.003,
        "SELL": 0.0025,
    },
    "CNC_GTT": {
        "BUY": 0.0035,
        "SELL": 0.0035,
    },

}
D_Factor = 0 #15.94
cost_factor_4 = 0

logging.basicConfig(level=logging.DEBUG)


class KiteTrader:
    def __init__(self, agent, client, order_frequency,
                 product_mode="MIS"):
        self.agent = agent

        self.max_buy = self.agent.max_buy
        self.max_sell = self.agent.max_sell
        self.balance = self.agent.initial_money

        self.queue_size = self.agent.window_size + 1
        self._queue = []
#1234
        self.action_window = 10
        self.o_window = 5
        self.buy_price_queue= []
        self.sell_price_queue= []
        self.actions_queue = []
    #    action_2 = "None"
    #    action_4 = "None"
    #    action_1 = "None"
    #    cost = 0
        self.close_data = 0
        self.min_quantity = 5
        self.target_profit = float(0)
        self.units_1 = 1
        self.units = 0
    #    trade_data = 0
    #    units_factor = 1
    #    units = 1*units_factor
    #    units = 1*units_factor
    #    units = 1
        self.quantity = 0
        self.buffer_quantity = 1

        self.inventory = []
#123
        self.inventory_sell = []
        self.bought_price = 0
        self.sold_price = 0
#1234
    #    action_1= ""
    #    action_2 = ""
    #    trade_data = ""
  

        self.kite_client = client
        self.order_frequency_min = order_frequency
        self.product_mode = product_mode

        if self.product_mode == 'CNC':
            self.order_maker = CNCMode(self.kite_client)
        elif self.product_mode == 'CNC_GTT':
            self.order_maker = GTTMode(self.kite_client)
        # else MIS mode
        else:
            self.order_maker = MISMode(self.kite_client)

    def reset(self):
        self.balance = self.agent.initial_money
        self.inventory = []
        self.quantity = 0

    def trade(self, data):
        action_1 = "None"
        action_stag = "None_wait"
    
        self.close_data = data[0]

        if len(self._queue) >= self.queue_size:
            self._queue.pop(0)
        self._queue.append(self.close_data)
        if len(self._queue) < self.queue_size:
            return {
                'status': 'data not enough to trade',
                'action': 'fail',
                'timestamp': str(datetime.now()),
            }
        predicted_action, buy = self.agent.predict(self._queue)
        cost = self._queue[-1]
        action, self.units = self._trade_on_prediction(predicted_action, buy, cost)

        mode = self.product_mode.split('_')[0]
        if action == 'buy':
               
            if LT_2[self.product_mode] == 1:            
                if PULL[self.product_mode] == 1:
                    if STAG[self.product_mode] == 0:
                        action_stag = "buy_wait"
                        trade_data_stag = cost
                        self.stag(action_stag, trade_data_stag) 
#                        return {
#                            'status': 'do nothing',
#                            'action': 'nothing',
#                            'balance': self.balance,
#                            'timestamp': str(datetime.now()),
#                        }

                    elif STAG[self.product_mode] == 1:
                                            action_1 = "buy"                
                                            buy_price = round(cost * (1 - COST_FACTORS[self.product_mode]["BUY"]),1) - cost_factor_4
                                            trade_data = buy_price
                                            self.orders_q(action_1, trade_data)
                    #                        action_2 = self.orders_q(action_1, trade_data)
                    #                         if action_2 == "buy":
                    #                             try:
                    #                                 order_id = self.order_maker.buy(buy_price, units, self.close_data)
                    #                             except Exception as e:
                    #                                 msg = "Order placement failed: {}".format(e)
                    #                                 logging.error(msg)
                    #                                 return {
                    #                                     'error': msg,
                    #                                     'balance': self.balance,
                    #                                     'timestamp': str(datetime.now()),
                    #                                 }
                                                
                    # #123 Added self.sold_price
                    #                             total_buy, self.sold_price = self.commit_buy(units, buy_price)
                    #                             #123 Added self.sold_price
                    #                             try:
                    #                                 invest = ((total_buy - self.sold_price) / self.sold_price) * 100
                    #                             except:
                    #                                 invest = 0
                                    
                    #                             msg = 'place an order %s to buy %d units at price %f' % (order_id, units, total_buy)
                    #                             print(msg)

                    #                             return {
                    #                                 'status': msg,
                    #                                 'units': units,
                    #                                 #123 
                    #                                 'investment': invest,
                    #                                 ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                    #                                 'gain': total_buy - self.sold_price,
                    #                                 'action': 'buy',
                    #                                 'balance': self.balance,
                    #                                 'timestamp': str(datetime.now()),
                    #                                 'order_id': order_id,
                    #                             }
                    #                         else:
                    #                             print('do nothing')
                    #sell_call
                
        elif action == 'sell':
            if LT_2[self.product_mode] == 2:
                if PULL[self.product_mode] == 2 :
                    if STAG[self.product_mode] == 0:
                            action_stag = "sell_wait"
                            trade_data_stag = cost
                            self.stag(action_stag, trade_data_stag)
                        #     return {
                        #     'status': 'do nothing',
                        #     'action': 'nothing',
                        #     'balance': self.balance,
                        #     'timestamp': str(datetime.now()),
                        # }

                    elif STAG[self.product_mode] == 1:
                                            action_1= "sell"               
                                            sell_price = round(cost * (1 + COST_FACTORS[self.product_mode]["SELL"]),1) + cost_factor_4
                                            trade_data = sell_price
                                            self.orders_q(action_1, trade_data)
                                            # action_2 = self.orders_q(action_1, trade_data)
                                            # if action_2 == "sell":    
                                            #     try:
                                                
                                            #         order_id = self.order_maker.sell(sell_price, units, self.close_data)
                                            #     except Exception as e:
                                            #         msg = "Order placement failed: {}".format(e)
                                            #         logging.error(msg)
                                            #         return {
                                            #             'error': msg,
                                            #             'balance': self.balance,
                                            #             'timestamp': str(datetime.now()),
                                            #         }
                                            #     ##do we need a bought price ? Needs to remove it (29_oct_20)
                                            #     total_sell, self.bought_price = self.commit_sell(units, sell_price)
                                            #     ##Ading a logic to improve the code when inventory <0 
                                            #     ## 
                                                
                                            #     try:
                                            #         invest = ((total_sell - self.bought_price) / self.bought_price) * 100
                                            #     except:
                                            #         invest = 0
                                    
                                            #     msg = 'place an order %s to sell %d units at price %f' % (order_id, units, total_sell)
                                            #     print(msg)

                                            #     return {
                                            #         'status': msg,
                                            #         'units': units,
                                            #         'investment': invest,
                                            #         ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                                            #         'gain': total_sell - self.bought_price,
                                            #         'balance': self.balance,
                                            #         'action': 'sell',
                                            #         'timestamp': str(datetime.now()),
                                            #         'order': order_id,
                                            #     }
                                            # else:
                                            #     print('do nothing')

       ##Added another pair of Pull & 'buy' and 'sell' api to this 
       ##Removed 
                     
        #return {
        #   'status': 'do nothing',
        #   'action': 'nothing',
        #   'balance': self.balance,
        #   'timestamp': str(datetime.now()),
        #}

        elif LT_2[self.product_mode] == 1:
            if PULL[self.product_mode] == 1:
                if STAG[self.product_mode] == 0:
                        action_stag = "buy_wait"
                        trade_data_stag = cost
                        self.stag(action_stag, trade_data_stag)

                        #     return {
                        #     'status': 'do nothing',
                        #     'action': 'nothing',
                        #     'balance': self.balance,
                        #     'timestamp': str(datetime.now()),
                        # }

                elif STAG[self.product_mode] == 1: 
                                        action_1= "buy"                
                                        buy_price = round(cost * (1 - COST_FACTORS[self.product_mode]["BUY"]),1) - cost_factor_4
                                        trade_data = buy_price
                                        self.orders_q(action_1, trade_data)
                #                         action_2 = self.orders_q(action_1, trade_data)
                #                         if action_2 == "buy":
                #                             try:
                #                                 order_id = self.order_maker.buy(buy_price, units, self.close_data)
                #                             except Exception as e:
                #                                 msg = "Order placement failed: {}".format(e)
                #                                 logging.error(msg)
                #                                 return {
                #                                     'error': msg,
                #                                     'balance': self.balance,
                #                                     'timestamp': str(datetime.now()),
                #                                 }
                                            
                # #123 Added self.sold_price
                #                             total_buy, self.sold_price = self.commit_buy(units, buy_price)
                #                             #123 Added self.sold_price
                #                             try:
                #                                 invest = ((total_buy - self.sold_price) / self.sold_price) * 100
                #                             except:
                #                                 invest = 0
                                
                #                             msg = 'place an order %s to buy %d units at price %f' % (order_id, units, total_buy)
                #                             print(msg)

                #                             return {
                #                                 'status': msg,
                #                                 'units': units,
                #                                 #123 
                #                                 'investment': invest,
                #                                 ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                #                                 'gain': total_buy - self.sold_price,
                #                                 'action': 'buy',
                #                                 'balance': self.balance,
                #                                 'timestamp': str(datetime.now()),
                #                                 'order_id': order_id,
                #                             }
                #                         else:
                #                             print('do nothing')
    #sell_call
        
        elif  LT_2[self.product_mode] == 2:
            if PULL[self.product_mode] == 2:      
                if STAG[self.product_mode] == 0:
                        action_stag = "sell_wait"
                        trade_data_stag = cost
                        self.stag(action_stag, trade_data_stag)
                    # return {
                    #             'status': 'do nothing',
                    #             'action': 'nothing',
                    #             'balance': self.balance,
                    #             'timestamp': str(datetime.now()),
                    #         }

                elif STAG[self.product_mode] == 1: 
                                        action_1 = "sell"               
                                        sell_price = round(cost * (1 + COST_FACTORS[self.product_mode]["SELL"]),1) + cost_factor_4
                                        trade_data = sell_price
                                        self.orders_q(action_1, trade_data)
                                        # action_2 = self.orders_q(action_1, trade_data)
                                        # if action_2 == "sell":    
                                        #     try:
                                            
                                        #         order_id = self.order_maker.sell(sell_price, units, self.close_data)
                                        #     except Exception as e:
                                        #         msg = "Order placement failed: {}".format(e)
                                        #         logging.error(msg)
                                        #         return {
                                        #             'error': msg,
                                        #             'balance': self.balance,
                                        #             'timestamp': str(datetime.now()),
                                        #         }
                                        #     ##do we need a bought price ? Needs to remove it (29_oct_20)
                                        #     total_sell, self.bought_price = self.commit_sell(units, sell_price)
                                        #     ##Ading a logic to improve the code when inventory <0 
                                        #     ## 
                                            
                                        #     try:
                                        #         invest = ((total_sell - self.bought_price) / self.bought_price) * 100
                                        #     except:
                                        #         invest = 0
                                
                                        #     msg = 'place an order %s to sell %d units at price %f' % (order_id, units, total_sell)
                                        #     print(msg)

                                        #     return {
                                        #         'status': msg,
                                        #         'units': units,
                                        #         'investment': invest,
                                        #         ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                                        #         'gain': total_sell - self.bought_price,
                                        #         'balance': self.balance,
                                        #         'action': 'sell',
                                        #         'timestamp': str(datetime.now()),
                                        #         'order': order_id,
                                        #     }
                                        # else:
                                        #     print('do nothing')
        
       ## Added a buy and sell call simultaneously to LT_2 = 0 added PULL == 1, 2, -1, -2
        elif LT_2[self.product_mode] == 0:
            if PULL[self.product_mode] == -1 or PULL[self.product_mode] == 1 :
                if STAG[self.product_mode] == 0:
                        action_stag = "buy_wait"
                        trade_data_stag = cost
                        self.stag(action_stag, trade_data_stag)
                    # return {
                    #         'status': 'do nothing',
                    #         'action': 'nothing',
                    #         'balance': self.balance,
                    #         'timestamp': str(datetime.now()),
                    #     }

                elif STAG[self.product_mode] == 1:   
                                        action_1= "buy"                
                                        buy_price = round(cost * (1 - COST_FACTORS[self.product_mode]["BUY"]),1) - cost_factor_4
                                        trade_data = buy_price
                                        self.orders_q(action_1, trade_data)
                #                         action_2 = self.orders_q(action_1, trade_data)
                #                         if action_2 == "buy":
                #                             try:
                #                                 order_id = self.order_maker.buy(buy_price, units, self.close_data)
                #                             except Exception as e:
                #                                 msg = "Order placement failed: {}".format(e)
                #                                 logging.error(msg)
                #                                 return {
                #                                     'error': msg,
                #                                     'balance': self.balance,
                #                                     'timestamp': str(datetime.now()),
                #                                 }
                                            
                # #123 Added self.sold_price
                #                             total_buy, self.sold_price = self.commit_buy(units, buy_price)
                #                             #123 Added self.sold_price
                #                             try:
                #                                 invest = ((total_buy - self.sold_price) / self.sold_price) * 100
                #                             except:
                #                                 invest = 0
                                
                #                             msg = 'place an order %s to buy %d units at price %f' % (order_id, units, total_buy)
                #                             print(msg)

                #                             return {
                #                                 'status': msg,
                #                                 'units': units,
                #                                 #123 
                #                                 'investment': invest,
                #                                 ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                #                                 'gain': total_buy - self.sold_price,
                #                                 'action': 'buy',
                #                                 'balance': self.balance,
                #                                 'timestamp': str(datetime.now()),
                #                                 'order_id': order_id,
                #                             }
                #                         else:
                #                             print('do nothing')
    #sell_call
                
                
            
            elif PULL[self.product_mode] == -2 or PULL[self.product_mode] == 2 :
                if STAG[self.product_mode] == 0:
                        action_stag = "sell_wait"
                        trade_data_stag = cost
                        self.stag(action_stag, trade_data_stag)
                        # return {
                        #     'status': 'do nothing',
                        #     'action': 'nothing',
                        #     'balance': self.balance,
                        #     'timestamp': str(datetime.now()),
                        # }

                elif STAG[self.product_mode] == 1:  
                                        action_1= "sell"               
                                        sell_price = round(cost * (1 + COST_FACTORS[self.product_mode]["SELL"]),1) + cost_factor_4
                                        trade_data = sell_price
                                        self.orders_q(action_1, trade_data)
                                        # action_2 = self.orders_q(action_1, trade_data)
                                        # if action_2 == "sell":    
                                        #     try:
                                            
                                        #         order_id = self.order_maker.sell(sell_price, units, self.close_data)
                                        #     except Exception as e:
                                        #         msg = "Order placement failed: {}".format(e)
                                        #         logging.error(msg)
                                        #         return {
                                        #             'error': msg,
                                        #             'balance': self.balance,
                                        #             'timestamp': str(datetime.now()),
                                        #         }
                                        #     ##do we need a bought price ? Needs to remove it (29_oct_20)
                                        #     total_sell, self.bought_price = self.commit_sell(units, sell_price)
                                        #     ##Ading a logic to improve the code when inventory <0 
                                        #     ## 
                                            
                                        #     try:
                                        #         invest = ((total_sell - self.bought_price) / self.bought_price) * 100
                                        #     except:
                                        #         invest = 0
                                
                                        #     msg = 'place an order %s to sell %d units at price %f' % (order_id, units, total_sell)
                                        #     print(msg)

                                        #     return {
                                        #         'status': msg,
                                        #         'units': units,
                                        #         'investment': invest,
                                        #         ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                                        #         'gain': total_sell - self.bought_price,
                                        #         'balance': self.balance,
                                        #         'action': 'sell',
                                        #         'timestamp': str(datetime.now()),
                                        #         'order': order_id,
                                        #     }
                                        # else:
                                        #     print('do nothing')

            elif LT_2[self.product_mode] == 1:
                if PULL[self.product_mode] == 0:
                    if STAG[self.product_mode] == 1:
                        action_stag = "buy_wait"
                        trade_data_stag = cost
                        self.stag(action_stag, trade_data_stag)
                        # return {
                        #     'status': 'do nothing',
                        #     'action': 'nothing',
                        #     'balance': self.balance,
                        #     'timestamp': str(datetime.now()),
                        # }
            elif LT_2[self.product_mode] == 2:
                if PULL[self.product_mode] == 0:
                    if STAG[self.product_mode] == 1:
                        action_stag = "sell_wait"
                        trade_data_stag = cost
                        self.stag(action_stag, trade_data_stag)
                        # return {
                        #     'status': 'do nothing',
                        #     'action': 'nothing',
                        #     'balance': self.balance,
                        #     'timestamp': str(datetime.now()),
                        # }



        # elif PULL[self.product_mode] == 0:
        #     return {
        #         'status': 'do nothing',
        #         'action': 'nothing',
        #         'balance': self.balance,
        #         'timestamp': str(datetime.now()),
        #     }

            
        

    # Is the last data value is really a cost?
    def _trade_on_prediction(self, action, buy, cost):
        if action == 1 and self.balance >= cost:
            if buy < 0:
                buy = self.units_1 #1
            if buy > self.max_buy:
                buy = self.units_1 #self.max_buy
            else:
                buy = self.units_1
    
            buy_units = buy
    #        buy_units = self.units_1

            return "buy", buy_units
        #changed the from -- 'len(self.inventory) > 0'  to 'len(self.inventory) > max_total_sell' (29_oct_20)
        elif action == 2 and len(self.inventory_sell) >= 0 and self.max_sell > 0:
            if self.quantity > self.max_sell:
                sell_units = self.units_1 #self.max_sell
            else:
                sell_units = self.units_1 #self.quantity
    #        sell_units = self.units_1

            return "sell", sell_units
            

        return "do nothing", 0

    def commit_buy(self, units, buy_price):
    #    global self.sold_price
        # total_buy = units * buy_price * (1 + CORR_FACTOR)
#123456 Moved to profits "buy"
    #    self.quantity += units
        total_buy = units * buy_price
        self.balance -= total_buy
  #     self.inventory.append(total_buy)
#        123 Added logic
#       for i in self.inventory(): 
#           if self.inventory[i] < 0:
#               self.sold_price = self.inventory.pop(-1)
#           elif self.inventory[i] >= 0:
#               self.inventory.append(total_buy)
#               self.sold_price = 0
#        123 Added logic modified
#       for i in self.inventory() and self.inventory_sell():
#                   if self.inventory[i] >= 0 and  self.inventory_sell[i] == 0:
#                                   self.inventory.append(total_buy)
#                                   self.sold_price = 0
#               elif self.inventory[i] >= 0 and  self.inventory_sell[i] > 0:
#                                   self.inventory.append(total_buy)
#                                   for v in self.inventory_sell():
#                                       if total_buy in v:
#                                           self.sold_price = v.remove(total_buy)
#                                       else:     
#                                           self.sold_price = self.inventory_sell.pop(0)
    #           elif self.inventory[i] > 0 and  self.inventory_sell[i] > 0:

        self.inventory.append(total_buy)
        if len(self.inventory_sell) == 0:
                self.sold_price = 0
        elif len(self.inventory_sell) > 0:
                self.sold_price = self.inventory_sell.pop(0)  
    #           for item in enumerate(self.inventory_sell):
    #               if int(total_buy) in item:
    #                   self.sold_price = item.remove(total_buy)
    #               else:     
    #                   self.sold_price = self.inventory.pop(0)                
                    
                        
    #    self.quantity += units
        return total_buy, self.sold_price

    def commit_sell(self, units, sell_price):
    #    global self.bought_price
# Moved to profits "sell"
    #    self.quantity -= units
        # total_sell = units * sell_price * (1 - CORR_FACTOR)
        total_sell = units * sell_price
        # For kite CNC
        # total_sell = (units * sell_price) - D_FACTOR
        self.balance += total_sell
#       self.bought_price = self.inventory.pop(0)
#       123 Added logic
#       for i in self.inventory(): 
#           if self.inventory[i] > 0:
#               self.bought_price = self.inventory.pop(0)
#           elif self.inventory[i] <= 0:
#               self.inventory.append(-total_sell) 
#               self.bought_price = 0
#        123 Added logic modified
# Replaced key with i=index for list[] function 
#   for i in self.inventory_sell() and self.inventory():
#                       if self.inventory_sell[i] >= 0 and  self.inventory[i] == 0:
#                                           self.inventory_sell.append(total_sell)
#                                           self.bought_price = 0
#                   elif self.inventory_sell[i] >= 0 and  self.inventory[i] > 0:
#                                       self.inventory_sell.append(total_sell)
#                                       for v in self.inventory():
#                                           if total_sell in v:
#                                               self.bought_price = v.remove(total_sell)
#                                           else:     
#                                               self.bought_price = self.inventory.pop(0)
        self.inventory_sell.append(total_sell)
        if len(self.inventory) == 0:
                    self.bought_price = 0
        elif len(self.inventory) > 0:
                    self.bought_price = self.inventory.pop(0)    
#               for item in enumerate(self.inventory):
#                   if int(total_sell) in item:
#                       self.bought_price = item.remove(total_sell)
#                   else:     
#                       self.bought_price = self.inventory.pop(0)                    
#        self.quantity -= units

        return total_sell, self.bought_price

## Check the order status and avoid making repeted orders at the same price .

    def orders_q(self, action_1, trade_data):
#        global action_2
#        self.action_window = 6
#        window = 3
#          self. self.buy_price_queue= []
#         self. self.sell_price_queue= []
#        self.actions_queue = []
#        action_1= action_1
        action_2 = "None"

        if len(self.actions_queue) <= self.action_window: 
            self.actions_queue.append(action_1)
            if action_1 == "buy":
                print("O_1")
        #            buy_price = trade_data
                if len(self.buy_price_queue) <= self.o_window :
                    self.buy_price_queue.append(trade_data)
                    action_2 = "buy"
            elif action_1== "sell":
                print("O_2")
        #               sell_price = trade_data
                if len(self.buy_price_queue) <= self.o_window :
                    self.sell_price_queue.append(trade_data)
                    action_2 = "sell"
                    
            
        elif len(self.actions_queue) >= self.action_window + 1 :
           
#123456  Moved to next
    #        self.actions_queue.append(action_1)
    #        self.actions_queue.pop(0) 
            if action_1== "buy":
    #            buy_price = trade_data
                if len(self.buy_price_queue) <= self.o_window :
                    print("O_3")
                    self.buy_price_queue.append(trade_data)
    #            self.buy_price_queue.pop(0)
                    action_2 = "buy"
#123456
                    self.actions_queue.append(action_2)
    #                self.actions_queue.pop(0) 
                elif len(self.buy_price_queue) >= self.o_window + 1 :
                  

    #                self.buy_price_queue.append(trade_data)
    #                self.buy_price_queue.pop(0)
        # [-2:]
                    if "buy" in  self.actions_queue[-1]:
                        print("O_4")
                    #Added [-3:] so that it sould not buy again for the same price 
                    ##Added difference so that you can get every order with 10 paisa difference
#                   Added and abs() function to tackle fluctuations in the Market so that it can buy at lower prices if wanted                    
                        if trade_data not in self.buy_price_queue[-3:] and (abs(trade_data - self.buy_price_queue[-1]) >= 0.095) :      
                    #    if trade_data not in self.buy_price_queue[-3:]: replaced with above                     
                                self.buy_price_queue.append(trade_data)
                                self.buy_price_queue.pop(0)
                                #Only going to append whn you are ready to take action 
    #                            self.actions_queue.append(action_1)
    #                            self.actions_queue.pop(0) 
                                action_2 = "buy"
                        else :  action_2 = "do nothing"
        # [-2:]                      
                    elif "sell" in  self.actions_queue[-1]:
                        print("O_5")                                                                    
                        if trade_data not in  self.sell_price_queue[-1:]:
                                self.buy_price_queue.append(trade_data)
                                self.buy_price_queue.pop(0)
                                #Only going to append whn you are ready to take action 
    #                            self.actions_queue.append(action_1)
    #                            self.actions_queue.pop(0) 
                                action_2 = "buy"
                        else :  action_2= "do nothing"
    #123456     Added  and then moved to profits              
                    # self.actions_queue.append(action_2)
                    # self.actions_queue.pop(0) 
                            
            elif action_1 == "sell":
    #            sell_price = trade_data
                if len(self.sell_price_queue) <= self.o_window :
                    print("O_6")                               
                    self.sell_price_queue.append(trade_data)
    #            self.sell_price_queue.pop(0)  
                    action_2 = "sell"
    #123456  Added
                    self.actions_queue.append(action_2)
    #                self.actions_queue.pop(0) 
                              
                elif len(self.sell_price_queue) >= self.o_window + 1 :
    #123456  Moved to next
    #                self.sell_price_queue.append(trade_data)
    #                self.sell_price_queue.pop(0)
        # [-2:]  
                    if "buy" in  self.actions_queue[-1]:
                            print("O_7")                                         
                            if trade_data not in  self.buy_price_queue[-1:]:
                                        self.sell_price_queue.pop(0)                                
                                        self.sell_price_queue.append(trade_data)
                                        #Only going to append whn you are ready to take action 
    #                                    self.actions_queue.append(action_1)
    #                                    self.actions_queue.pop(0)     
                                        action_2 = "sell"
                            else :      action_2 = "do nothing"
        # [-2:]     #Added [-3:] so that it sould not buy again for the same price 
                    ##Added difference so that you can get every order with 10 paisa difference 
#                   Added and abs() function to tackle fluctuations in the Market so that it can sell at higher prices if wanted        
                    elif "sell" in  self.actions_queue[-1] and (abs(trade_data - self.sell_price_queue[-1]) >= 0.095) :
                            print("O_8")  
                    #      elif "sell" in  self.actions_queue[-2]: replaced with above
                            if trade_data not in  self.sell_price_queue[-3:]:                                                                     
                                        self.sell_price_queue.pop(0)                                
                                        self.sell_price_queue.append(trade_data)
                                        #Only going to append whn you are ready to take action 
    #                                    self.actions_queue.append(action_1)
    #                                    self.actions_queue.pop(0)     
                                        action_2 = "sell"
                            else :      action_2 = "do nothing"
    #123456 Added here and moved to orders_q
                    # self.actions_queue.append(action_2)
                    # self.actions_queue.pop(0)                                  
            else:
                print('Conditions are not met. action_1val : ',action_1)
                
        self.profits(action_2, trade_data)
        
    #    print(action_1, trade_data)    
        print("action_1=", action_1, "action_2= ", action_2, +123, self.actions_queue,  self.buy_price_queue,  self.sell_price_queue)
        print("orders_q session------------------------------") 
        return action_2
    
    
    def profits(self, action_2, trade_data):
    #    global action_4, units
    #    trade_data = 195.5
    #    buy_price_queue = [195, 195.2, 195.4, 195.5]
    #    buy_price_queue_window = 3
    #    average_buy_price = 0
    #    average_buy_price_window = 1
        
    #    sell_price_queue = [195.6, 195.55, 195.5, 195.65]
    #    sell_price_queue_window = 3
    #    average_sell_price = 0
    #    average_sell_price_window = 1
        
    #    inventory = [] 
    #    sell_inventory = []
    #    invest = 0
    #    action_2 = "buy"
    #    action_4 = "None"
    #    profits = s.mean(self.sell_price_queue) - s.mean(self.buy_price_queue)
        profits = float(0)
        average_buy_price = 0
        average_sell_price = 0
        action_profits = "None"
        #12345
    #    buy_price = 0
    #    sell_price = 0
        new_price = 0
        units = 0
    #    quantity = 4
        
#        self.close_data = 195.5 
        
        if action_2 == "buy":
            if len(self.buy_price_queue) <= self.o_window:
##12345 inserted a buy call for the action_2 = buy for regular orders to get executed        
#                buy_price = round(cost * (1 - COST_FACTORS[self.product_mode]["BUY"]),1) - cost_factor_4
                action_profits = "buy"
#                action_2 = self.orders_q(action_1, trade_data)
                buy_price = trade_data 
                units = self.units

                try:
                    order_id = self.order_maker.buy(buy_price, units, self.close_data)
                except Exception as e:
                    msg = "Order placement failed: {}".format(e)
                    logging.error(msg)
                    return {
                        'error': msg,
                        'balance': self.balance,
                        'timestamp': str(datetime.now()),
                    }
                
#123 Added self.sold_price
                total_buy, self.sold_price = self.commit_buy(units, buy_price)
#123456   Moveed here from commit_buy             
                self.quantity += units
                #123 Added self.sold_price
                try:
                    invest = ((total_buy - self.sold_price) / self.sold_price) * 100
                except:
                    invest = 0
    
                msg = 'place an order %s to buy %d units at price %f' % (order_id, units, total_buy)
                print(msg)

                return {
                    'status': msg,
                    'units': units,
                    #123 
                    'investment': invest,
                    ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                    'gain': total_buy - self.sold_price,
                    'action': 'buy',
                    'balance': self.balance,
                    'timestamp': str(datetime.now()),
                    'order_id': order_id,
                }
            

            elif len(self.buy_price_queue) >= self.o_window + 1:
                print("A")
    #123456 moved here from orders_q            
                self.actions_queue.append(action_2)
                self.actions_queue.pop(0) 

                average_buy_price = s.mean(self.buy_price_queue[:-1])
        #        buy_price_queue.pop(0)
        #        buy_price_queue.append(trade_data)

    #            for i in inventory: 
    #                if inventory[i] == 0:
    #                    invest == 0  
    #                elif inventory[i] > 0:
                # profit = avergae_buy_price < self.close_data 
                #        invest = (((self.close_data - average_buy_price ))/(average_buy_price))*100
    #789  muted  "buy" in self.actions_queue [-4:]:          
    #            if self.quantity > self.min_quantity and "buy" in self.actions_queue [-4:]:
                if self.quantity > self.min_quantity:    
                        profits = trade_data - average_buy_price
                        if profits >= 0.25:
                            new_price = trade_data
                        #    return buy_price
                        elif profits <= 0.25:
                            self.target_profit = 0.3 - profits 
                            new_price = trade_data + self.target_profit

##12345 action_profits is added to append the action taken  into the action_queue list                 
                        action_profits = "sell"
##12345 removes the last action in action_queue which is added in orders_q fun() line 699, 711, 712 and replaced it with the current action same applies for the price
                        self.actions_queue.pop(-1) 
                        self.actions_queue.append(action_profits)        
                        self.buy_price_queue.pop(-1)
                        self.sell_price_queue.append(new_price)
                        sell_price = new_price
#789
                        units = abs(self.quantity) - self.buffer_quantity
                       
                        try:
                        #pulling cost as buy_rpice and sell_rpice respectively
#                            sell_price = new_price
#                            units = self.quantity        
                            order_id = self.order_maker.sell(sell_price, units, self.close_data)
                        except Exception as e:
                                msg = "Order placement failed: {}".format(e)
                                logging.error(msg)
                                return {
                                    'error': msg,
                                    'balance': self.balance,
                                    'timestamp': str(datetime.now()),
                                }
                            ##do we need a bought price ? Needs to remove it (29_oct_20)
                        total_sell, self.bought_price = self.commit_sell(units, sell_price)
#Moved here from commit_sell                        
                        self.quantity -= units 
                        ##Ading a logic to improve the code when inventory <0 
                        ##                         
                        try:
                            invest = ((total_sell - self.bought_price) / self.bought_price) * 100
                        except:
                            invest = 0
            
                        msg = 'place an order %s to sell %d units at price %f' % (order_id, units, total_sell)
                        print(msg)

                        return {
                            'status': msg,
                            'units': units,
                            'investment': invest,
                            'gain': total_sell - self.bought_price,
                            'balance': self.balance,
                            'action': 'sell',
                            'timestamp': str(datetime.now()),
                            'order': order_id,
                        }


##12345 inserted the below function and buy call  
# Replaced 0 with  - self.min_quantity in elif  0 >= self.quantity < self.min_quantity :                        
# Replaced with below  
#                elif -self.min_quantity >= self.quantity <= self.min_quantity :
#                elif self.quantity >= -self.min_quantity and self.quantity <= self.min_quantity :
                elif self.quantity <= self.min_quantity :
                    print("B")      
                    action_profits = "buy"
    #                action_2 = self.orders_q(action_1, trade_data)
                    buy_price = trade_data
                    units = self.units

                    try:
                        order_id = self.order_maker.buy(buy_price, units, self.close_data)
                    except Exception as e:
                        msg = "Order placement failed: {}".format(e)
                        logging.error(msg)
                        return {
                            'error': msg,
                            'balance': self.balance,
                            'timestamp': str(datetime.now()),
                        }
                    
#123 Added self.sold_price
                    total_buy, self.sold_price = self.commit_buy(units, buy_price)
#123456   Moveed here from commit_buy             
                    self.quantity += units
#123 Added self.sold_price
                    try:
                        invest = ((total_buy - self.sold_price) / self.sold_price) * 100
                    except:
                        invest = 0
        
                    msg = 'place an order %s to buy %d units at price %f' % (order_id, units, total_buy)
                    print(msg)

                    return {
                        'status': msg,
                        'units': units,
#123 
                        'investment': invest,
##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                        'gain': total_buy - self.sold_price,
                        'action': 'buy',
                        'balance': self.balance,
                        'timestamp': str(datetime.now()),
                        'order_id': order_id,
                    }
                    
#                else : print('do nothing') #action_4 = "do nothing"                      
#                elif inventory[i] < 0:
            #        invest = ((total_sell - self.bought_price) / self.bought_price) * 10
            #        invest = (((self.close_data - average_sell_price )*units)/(average_sell_price*units))*100
            
        elif action_2 == "sell":
            if len(self.sell_price_queue) <= self.o_window:
##12345 inserted a sell call for the action_2 = sell for regular orders to get executed     
#                sell_price = round(cost * (1 + COST_FACTORS[self.product_mode]["SELL"]),1) + cost_factor_4
                action_profits = "sell"
#                action_2 = self.orders_q(action_1, trade_data)
                sell_price  = trade_data 
                units = self.units
                try:                    
                    order_id = self.order_maker.sell(sell_price, units, self.close_data)
                except Exception as e:
                    msg = "Order placement failed: {}".format(e)
                    logging.error(msg)
                    return {
                        'error': msg,
                        'balance': self.balance,
                        'timestamp': str(datetime.now()),
                    }
##do we need a bought price ? Needs to remove it (29_oct_20)
                total_sell, self.bought_price = self.commit_sell(units, sell_price)
#123456   Moveed here from commit_sell           
                self.quantity -= units
##Ading a logic to improve the code when inventory <0 
                
                try:
                    invest = ((total_sell - self.bought_price) / self.bought_price) * 100
                except:
                    invest = 0
    
                msg = 'place an order %s to sell %d units at price %f' % (order_id, units, total_sell)
                print(msg)

                return {
                    'status': msg,
                    'units': units,
                    'investment': invest,
                    ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                    'gain': total_sell - self.bought_price,
                    'balance': self.balance,
                    'action': 'sell',
                    'timestamp': str(datetime.now()),
                    'order': order_id,
                }

            elif len(self.sell_price_queue) >= self.o_window + 1:
                print("C")
    #123456 MOved here from orders_q
                self.actions_queue.append(action_2)
                self.actions_queue.pop(0)    

                average_sell_price = s.mean(self.sell_price_queue[:-1])
        #        sell_price_queue.pop(0)
        #        sell_price_queue.append(trade_data)
#789 Muted "sell" in self.actions_queue [-4:]:     
#                if self.quantity < -self.min_quantity  and "sell" in self.actions_queue [-4:]:
                if self.quantity < (-self.min_quantity):
                    ##Replaced self.close_data with trade_data 
                    #self._queue[-1] replaced with trade_data     
                    profits =  average_sell_price - trade_data
                    if profits >= 0.25:
                        new_price = trade_data
                    #    return buy_price
                    elif profits <= 0.25:
                        self.target_profit = 0.3 - profits 
                        new_price = trade_data + self.target_profit
#12345 added the new variable action_profits to deifne the actions taken       
                    action_profits = "buy"
##12345removes the last action in action_queue which is added in orders_q fun() line 699, 711, 712 and replaced it with the current action same applies for the price
                    self.actions_queue.pop(-1) 
                    self.actions_queue.append(action_profits)        
                    self.sell_price_queue.pop(-1)
                    self.buy_price_queue.append(new_price)
                    buy_price = new_price
#789 
                    units = abs(self.quantity) - self.buffer_quantity

                    try:
#                        buy_price = new_price
#                        units = self.quantity  
                        order_id = self.order_maker.buy(buy_price, units, self.close_data)
                    except Exception as e:
                        msg = "Order placement failed: {}".format(e)
                        logging.error(msg)
                        return {
                            'error': msg,
                            'balance': self.balance,
                            'timestamp': str(datetime.now()),
                        }
                    
#123 Added self.sold_price
                    total_buy, self.sold_price = self.commit_buy(units, buy_price)
#123456   Moveed here from commit_buy             
                    self.quantity += units 
                    #123 Added self.sold_price
                    try:
                        invest = ((total_buy - self.sold_price) / self.sold_price) * 100
                    except:
                        invest = 0
        
                    msg = 'place an order %s to buy %d units at price %f' % (order_id, units, total_buy)
                    print(msg)

                    return {
                        'status': msg,
                        'units': units,
                        #123 
                        'investment': invest,
                        ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                        'gain': total_buy - self.sold_price,
                        'action': 'buy',
                        'balance': self.balance,
                        'timestamp': str(datetime.now()),
                        'order_id': order_id,
                    }

##12345 inserted the below function and sell call
# Replaced with below  
#                elif  self.min_quantity >= self.quantity >= -self.min_quantity :
                elif self.quantity >= (-self.min_quantity) and self.quantity <= self.min_quantity :
                    print("D")
                    action_profits = "sell"                 
#                action_2 = self.orders_q(action_1, trade_data) 
                    sell_price = trade_data  
                    units = self.units
                    try:    
                        # sell_price = trade_data  
                        # units = self.units                
                        order_id = self.order_maker.sell(sell_price, units, self.close_data)
                    except Exception as e:
                        msg = "Order placement failed: {}".format(e)
                        logging.error(msg)
                        return {
                            'error': msg,
                            'balance': self.balance,
                            'timestamp': str(datetime.now()),
                        }
                    ##do we need a bought price ? Needs to remove it (29_oct_20)
                    total_sell, self.bought_price = self.commit_sell(units, sell_price)
                    ##Ading a logic to improve the code when inventory <0 
#123456   Moveed here from commit_sell            
                    self.quantity -= units
                    try:
                        invest = ((total_sell - self.bought_price) / self.bought_price) * 100
                    except:
                        invest = 0
        
                    msg = 'place an order %s to sell %d units at price %f' % (order_id, units, total_sell)
                    print(msg)

                    return {
                        'status': msg,
                        'units': units,
                        'investment': invest,
                        ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                        'gain': total_sell - self.bought_price,
                        'balance': self.balance,
                        'action': 'sell',
                        'timestamp': str(datetime.now()),
                        'order': order_id,
                    }
    
  
        print('units=', units, 'quantity = ',self.quantity,'profits = ', profits, 'trade_data = ', trade_data, 'average_buy_price = ', average_buy_price, 'average_sell_price = ',average_sell_price, "new_price=", new_price, "target_profits=", self.target_profit, +1234)
        print("action_profits=", action_profits)
        print("Profit session------------------------------")
    #    return action_4 
    
                  
    def stag(self, action_stag, trade_data_stag):
        
        action_stag_1 = "None"
        units = 0
        if action_stag == "buy_wait":
            if len(self.buy_price_queue) <= self.o_window:
                print("stag_nothing")


            elif len(self.buy_price_queue) >= self.o_window + 1:
#Muted the below function because market can get into stagnation phase any time so no matter of profits ? or shall we consider profits ?
#                average_buy_price = s.mean(self.buy_price_queue[:-1])
#789 Muted the "buy" in self.actions_queue [-4:]:
#                if self.quantity > self.min_quantity and "buy" in self.actions_queue [-4:]:
                if self.quantity > self.min_quantity:
#12345 added the new variable action_stag_1 to deifne the actions taken                     
                    action_stag_1 = "sell"
#12345 Since the actions are coming straight forward by-pasiing the orders_q function() we need not to pop(-1) for both actions_queue and price_queue
#                    self.actions_queue.pop(-1) 
                    self.actions_queue.append(action_stag_1)        
#                    sell_price_queue.pop(-1)
                    self.sell_price_queue.append(trade_data_stag)
                    sell_price  = trade_data_stag
#789
                    units = abs(self.quantity)  - self.buffer_quantity
                    try:
#                        sell_price  = trade_data_stag
#                        units = self.quantity        
                        order_id = self.order_maker.sell(sell_price, units, self.close_data)
                    except Exception as e:
                            msg = "Order placement failed: {}".format(e)
                            logging.error(msg)
                            return {
                                'error': msg,
                                'balance': self.balance,
                                'timestamp': str(datetime.now()),
                            }
                        ##do we need a bought price ? Needs to remove it (29_oct_20)
                    total_sell, self.bought_price = self.commit_sell(units, sell_price)
#123456   Moveed here from commit_sell            
                    self.quantity -= units   
                    ##Ading a logic to improve the code when inventory <0 
                               
                    try:
                        invest = ((total_sell - self.bought_price) / self.bought_price) * 100
                    except:
                        invest = 0
        
                    msg = 'place an order %s to sell %d units at price %f' % (order_id, units, total_sell)
                    print(msg)

                    return {
                        'status': msg,
                        'units': units,
                        'investment': invest,
                        'gain': total_sell - self.bought_price,
                        'balance': self.balance,
                        'action': 'sell',
                        'timestamp': str(datetime.now()),
                        'order': order_id,
                    }

                else:
                    print("stag_nothing")


        elif action_stag == "sell_wait":
            if len(self.sell_price_queue) <= self.o_window:
                 print("stag_nothing")

            elif len(self.sell_price_queue) >= self.o_window + 1:
#Muted the below function because market can get into stagnation phase any time so no matter of profits ? or shall we consider profits ?
#                average_sell_price = s.mean(self.sell_price_queue[:-1])
        #        sell_price_queue.pop(0)
        #        sell_price_queue.append(trade_data)
#789 Muted --"sell" in self.actions_queue [-4:]:
#                if self.quantity < -self.min_quantity  and "sell" in self.actions_queue [-4:]:
                if self.quantity < (-self.min_quantity):
#12345 added the new variable action_stag_1 to deifne the actions taken    
                    action_stag_1 = "buy"
#12345 Since the actions are coming straight forward by pasiing the orders_q function() we need not to pop(-1) for both actions_queue and price_queue
#                    self.actions_queue.pop(-1) 
                    self.actions_queue.append(action_stag_1)        
#                    sell_price_queue.pop(-1)
                    self.buy_price_queue.append(trade_data_stag)
                    buy_price = trade_data_stag
                    units = abs(self.quantity) - self.buffer_quantity
                    try:
                        # buy_price = trade_data_stag
                        # units = self.quantity  
                        order_id = self.order_maker.buy(buy_price, units, self.close_data)
                    except Exception as e:
                        msg = "Order placement failed: {}".format(e)
                        logging.error(msg)
                        return {
                            'error': msg,
                            'balance': self.balance,
                            'timestamp': str(datetime.now()),
                        }
                    
#123 Added self.sold_price
                    total_buy, self.sold_price = self.commit_buy(units, buy_price)
#123456   Moveed here from commit_buy            
                    self.quantity += units 
#                    123 Added self.sold_price
                    try:
                        invest = ((total_buy - self.sold_price) / self.sold_price) * 100
                    except:
                        invest = 0
        
                    msg = 'place an order %s to buy %d units at price %f' % (order_id, units, total_buy)
                    print(msg)

                    return {
                        'status': msg,
                        'units': units,
                        #123 
                        'investment': invest,
                        ##improve the the code as 'gain' = total_sell - (cost*units) or 'gain': total_sell - self.bought_price . because you can't use the logic of 'if len(self.inventory) < 0:' here in return statement (29_oct_20)
                        'gain': total_buy - self.sold_price,
                        'action': 'buy',
                        'balance': self.balance,
                        'timestamp': str(datetime.now()),
                        'order_id': order_id,
                    }

                else:
                    print("stag_nothing")
                    
        print("action_stag=",action_stag, "action_stag_1=", action_stag_1, "units=", units)
        print("STAG session------------------------------")
    





        
        
    