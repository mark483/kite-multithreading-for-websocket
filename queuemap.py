from collections import defaultdict,OrderedDict
from setup_logger import logger
import time
import numpy as np
import talib
import math
import statistics as s

class InstrumentObject():
    def getName(self):
       return self.name

    def getValue(self):
       return self.value
    
    def getPrice(self):
        return self.trade_list[0]

    def __init__(self):
       self.price_list = []
       self.quantity_list = []
       self.price_sum = 0
       self.value_average = 0

    def add(self, price, quantity):
        self.price_list.insert(0, price)
        self.quantity_list.insert(0, quantity)
    
    def pop(self):
        if len(self.price_list)==1:
            self.price_list.insert(0, 0)
            self.quantity_list.insert(0, 0)
            self.price_list.pop()
            self.quantity_list.pop()
        else:
            self.price_list.pop()
            self.quantity_list.pop()


class QueueMap(object):

    def __init__(self, window):
        self._store = defaultdict(InstrumentObject)
        self.init_time = 0
        self.window = window

    def set(self, name, price, quantity):
        if self.init_time == 0:
            self.init_time = time.time()
        self._store[name].add(price,quantity)
        #logger.info(self._store[name].price_list)
        

    def check_window(self):
        #logger.info(time.time() - self.init_time)
        if (time.time() - self.init_time) >= self.window :
            logger.info('time started')  
            for key, value in self._store.items():
                self._store[key].price_sum = self.price_rocp_factor(value.price_list,len(value.price_list))
                self._store[key].value_average = self.traded_value(value.price_list,value.quantity_list)
                self._store[key].pop()
            self.init_time=time.time()
            logger.info('timer restarted')
            priceDict= {key: value for (key, value) in self._store.items() if not (math.isnan(value.price_sum) or value.value_average==0) }
            #logger.info(priceDict)
            if priceDict and len(priceDict)>=10:
                sorted_priceDict=sorted(priceDict.items(), key=lambda pair: pair[1].value_average, reverse=True)[:10]
                #logger.info(sorted_priceDict)
                priceDict = OrderedDict(sorted_priceDict)   
                return priceDict
        return None

    def price_rocp_factor(self, data,timeperiod) :
        if timeperiod==1:
            self.sum = talib.ROCP(np.array(data, dtype=np.float), timeperiod=1)[-1]
        else:
            self.sum = talib.ROCP(np.array(data, dtype=np.float), timeperiod=timeperiod-1)[-1]

        return self.sum

    def traded_value(self, price_data, quant_data) :
#multiply the data in real time to get the value 
        value_data = [a*b for a,b in zip(price_data,quant_data)]
        value_average = s.mean(value_data)

        return value_average