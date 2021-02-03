from datetime import datetime

from binance_api.Orders import Orders

CORR_FACTOR = 0.0008
COST_FACTOR = 0.0008


class BinanceTrader:
    def __init__(self, agent, corr_factor=CORR_FACTOR):
        self.agent = agent

        self.max_buy = self.agent.max_buy
        self.max_sell = self.agent.max_sell
        self.balance = self.agent.initial_money

        self.queue_size = self.agent.window_size + 1
        self._queue = []

        self.inventory = []
        self.quantity = 0

        self.corr_factor = corr_factor

    def trade(self, data):
        close_data = data[0]

        if len(self._queue) >= self.queue_size:
            self._queue.pop(0)
        self._queue.append(close_data)
        if len(self._queue) < self.queue_size:
            return {
                'status': 'data not enough to trade',
                'action': 'fail',
                'timestamp': str(datetime.now()),
            }
        # The below function generating Error 'Agent' object has no Arribute 'predict'
        predicted_action, buy = self.agent.predict(self._queue)
        cost = self._queue[-1]
        action, units = self._trade_on_prediction(predicted_action, buy, cost)

        if action == 'buy':
            # ToDo We should run it asynchronuously
            order, err = Orders.buy_market(symbol='BNBUSDT', quantity=units)
            # Added a buy_limit function 
            #  order, err = Orders.buy_limit(symbol='BNBUSDT', quantity=units, buy_price=cost*(1-COST_FACTOR)
            if err:
                print(err)
                return {
                    'balance': self.balance,
                    'timestamp': str(datetime.now()),
                    'order': order,
                }

            print('bought %d units' % units)
            total_buy = self.commit_buy(units, cost)
            return {
                'status': 'buy %d unit(s) at price %f' % (units, total_buy),
                'units': units,
                'action': 'buy',
                'balance': self.balance,
                'timestamp': str(datetime.now()),
                'order': order,
            }
        elif action == 'sell':
            order, err = Orders.sell_market(symbol='BNBUSDT', quantity=units)
            # Added a sell_limit function
            # order, err = Orders.sell_limit(symbol='BNBUSDT', quantity=units, sell_price=cost*(1+COST_FACTOR)
            if err:
                print(err)
                return {
                    'balance': self.balance,
                    'timestamp': str(datetime.now()),
                    'order': order,
                }

            print('sold %d units' % units)
            total_sell, bought_price = self.commit_sell(units, cost)

            try:
                invest = ((total_sell - bought_price) / bought_price) * 100
            except:
                invest = 0
            return {
                'status': 'sell %d unit(s) at price %f' % (units, total_sell),
                'units': units,
                'investment': invest,
                'gain': total_sell - bought_price,
                'balance': self.balance,
                'action': 'sell',
                'timestamp': str(datetime.now()),
                'order': order,
            }
        return {
            'status': 'do nothing',
            'action': 'nothing',
            'balance': self.balance,
            'timestamp': str(datetime.now()),
        }

    # Is the last data value is really a cost?
    def _trade_on_prediction(self, action, buy, cost):
        if action == 1 and self.balance >= cost:
            if buy < 0:
                buy = 1
            if buy > self.max_buy:
                buy_units = self.max_buy
            else:
                buy_units = buy

            return "buy", buy_units

        elif action == 2 and len(self.inventory) > 0 and self.max_sell > 0:
            if self.quantity > self.max_sell:
                sell_units = self.max_sell
            else:
                sell_units = self.quantity

            return "sell", sell_units

        return "do nothing", 0

    def commit_buy(self, buy_units, cost):
        total_buy = buy_units * cost * (1 + self.corr_factor)
        self.balance -= total_buy
        self.inventory.append(total_buy)
        self.quantity += buy_units

        return total_buy

    def commit_sell(self, sell_units, cost):
        total_sell = sell_units * cost * (1 - self.corr_factor)
        self.balance += total_sell
        bought_price = self.inventory.pop(0)
        self.quantity -= sell_units

        return total_sell, bought_price
