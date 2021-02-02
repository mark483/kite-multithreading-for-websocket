import logging

from kiteconnect import KiteConnect

GTT_FACTOR = 0.10
units_factor_GTT = 1
units_factor_CNC = 1
units_factor_MIS = 1

# units_factor = 1
# buy_units = 1*units_factor
# sell_units = 1*units_factor

logging.basicConfig(level=logging.DEBUG)


class GTTMode:
    def __init__(self, client):
        self.client = client

    def buy(self, buy_price, units, close_data):
        result = self.client.place_gtt(
            trigger_type=KiteConnect.GTT_TYPE_SINGLE,
            tradingsymbol='SBIN',
            exchange=KiteConnect.EXCHANGE_NSE,
            trigger_values=[buy_price + GTT_FACTOR],
            last_price=close_data,
            orders=[{
                'transaction_type': KiteConnect.TRANSACTION_TYPE_BUY,
                'quantity': units_factor_GTT*units,
                'price': buy_price,
                'order_type': KiteConnect.ORDER_TYPE_LIMIT,
                'product': KiteConnect.PRODUCT_CNC,
        }]
        )
        logging.info('Place GTT buy order with result: {} at trigger price {}'.format(
            result, buy_price + GTT_FACTOR))
        return result

    def sell(self, sell_price, units, close_data):
        result = self.client.place_gtt(
            trigger_type=KiteConnect.GTT_TYPE_SINGLE,
            tradingsymbol='SBIN',
            exchange=KiteConnect.EXCHANGE_NSE,
            trigger_values=[sell_price - GTT_FACTOR],
            last_price=close_data,
            orders=[{
                'transaction_type': KiteConnect.TRANSACTION_TYPE_SELL,
                'quantity':  units_factor_GTT*units,
                'price': sell_price,
                'order_type': KiteConnect.ORDER_TYPE_LIMIT,
                'product': KiteConnect.PRODUCT_CNC,
            }]
        )
        logging.info('Place GTT sell order with result: {} at trigger price {}'.format(
            result, sell_price - GTT_FACTOR))
        return result


class CNCMode:
    def __init__(self, client):
        self.client = client

    def buy(self, buy_price, units, _):
        order_id = self.client.place_order(
            variety=KiteConnect.VARIETY_REGULAR,
            tradingsymbol='SBIN',
            exchange=KiteConnect.EXCHANGE_NSE,
            transaction_type=KiteConnect.TRANSACTION_TYPE_BUY,
            quantity=units_factor_CNC*units,
            order_type=KiteConnect.ORDER_TYPE_LIMIT,
            price=buy_price,
            product=KiteConnect.PRODUCT_CNC)

        logging.info("CNC Order placed. ID is: {}".format(order_id))
        return order_id

    def sell(self, sell_price, units, _):
        order_id = self.client.place_order(
            variety=KiteConnect.VARIETY_REGULAR,
            tradingsymbol='SBIN',
            exchange=KiteConnect.EXCHANGE_NSE,
            transaction_type=KiteConnect.TRANSACTION_TYPE_SELL,
            quantity=units_factor_CNC*units,
            order_type=KiteConnect.ORDER_TYPE_LIMIT,
            price=sell_price,
            product=KiteConnect.PRODUCT_CNC)

        logging.info("CNC Order placed. ID is: {}".format(order_id))
        return order_id


class MISMode:
    def __init__(self, client):
        self.client = client

    def buy(self, buy_price, units, _):
        order_id = self.client.place_order(
            variety=KiteConnect.VARIETY_REGULAR,
            tradingsymbol='SBIN',
            exchange=KiteConnect.EXCHANGE_NSE,
            transaction_type=KiteConnect.TRANSACTION_TYPE_BUY,
            quantity=units_factor_MIS*units,# units_factor_MIS, #buy_units, ##units_factor_MIS*units,
            order_type=KiteConnect.ORDER_TYPE_LIMIT,
            price=buy_price,
            product=KiteConnect.PRODUCT_MIS)

        logging.info("MIS Order placed. ID is: {}".format(order_id))
        return order_id

    def sell(self, sell_price, units, _):
        order_id = self.client.place_order(
            variety=KiteConnect.VARIETY_REGULAR,
            tradingsymbol='SBIN',
            exchange=KiteConnect.EXCHANGE_NSE,
            transaction_type=KiteConnect.TRANSACTION_TYPE_SELL,
            quantity= units_factor_MIS*units,#units_factor_MIS, # sell_units, ##units_factor_MIS*units,
            order_type=KiteConnect.ORDER_TYPE_LIMIT,
            price=sell_price,
            product=KiteConnect.PRODUCT_MIS)

        logging.info("MIS Order placed. ID is: {}".format(order_id))
        return order_id
