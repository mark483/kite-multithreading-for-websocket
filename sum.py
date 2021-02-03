##Corrector has modifies the self.cost_factor_1 & self.cost_factor_2 using the rocp.

import logging
import numpy as np
import talib

logging.basicConfig(level=logging.DEBUG)


class Corrector :
    def __init__(self, mode, window, order_mode) :
        #self.mode = mode
        self.window = 30
        #self.order_mode = order_mode
        self._queue = []
        self.sum = 0

    def adjust_rocp_factor(self, data) :
    #    global self.cost_factor_1, self.cost_factor_2, self.pull
        close_data = data[0]
        self._queue.append(close_data)

        if len(self._queue) == self.window + 1 :
            self.sum = talib.ROCP(np.array(self._queue, dtype=np.float), timeperiod=self.window)[-1]
            self._queue.pop(0)

        logging.debug('rocp factor: {}'.format(self.sum))
   

        return self.sum
    

