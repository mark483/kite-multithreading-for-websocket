##Corrector has modifies the self.cost_factor_1 & self.cost_factor_2 using the rocp.
import statistics as s
import logging
import numpy as np
import talib

logging.basicConfig(level=logging.DEBUG)


class Sum:
    def __init__(self, mode, window, order_mode) :
        self.mode = mode
        self.window = window 
        self.order_mode = order_mode
        
        self.price_queue = []
        self.quant_queue = []
        self.value_queue = []
        
        self.price_sum = 0
        self.quant_sum = 0
        self.value_average = 0
        
        
        

    def price_rocp_factor(self, data) :
#sending the 1st index of the data price_queue
        price_data = data[0]
        self._queue.append(price_data)

        if len(self._queue) == self.window + 1 :
            self.sum = talib.ROCP(np.array(self._queue, dtype=np.float), timeperiod=self.window)[-1]
            self._queue.pop(0)

        logging.debug('price_rocp factor: {}'.format(self.sum))

        return self.price_sum
    
    def quant_rocp_factor(self, data) :
#sending the 2nd index of the data quant_queue
        quant_data = data[1]
        self.quant_queue.append(quant_data)

        if len(self.quant_queue) == self.window + 1 :
            self.sum = talib.ROCP(np.array(self.quant_queue, dtype=np.float), timeperiod=self.window)[-1]
            self.quant_queue.pop(0)

        logging.debug('quant_rocp factor: {}'.format(self.quant_sum))
   

        return self.quant_sum
    
    def traded_value(self, data) :
#multiply the data in real time to get the value 
        value_data = data[0]*data[1]
        self.value_queue.append(value_data)

        if len(self.value_queue) == self.window + 1 :
            self.value_average = s.mean(self.value_queue)
            self.value_queue.pop(0)

        logging.debug('value_average factor: {}'.format(self.value_average))
   

        return self.value_average