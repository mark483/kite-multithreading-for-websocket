import logging


def _cancel_pending_orders(client, orders):
    pending = [(order['variety'], order['order_id'])
               for order in orders if 'OPEN' in order['status']]

    # ToDo: if doesn't work in time, try to run it async.
    for p in pending:
        try:
            order_id = client.cancel_order(*p)
            logging.info('Order {} was canceled'.format(order_id))
        except Exception as err:
            logging.error(err)


def _handle_quantity_diff(client, quantity_diff):
    if quantity_diff > 0:
        try:
            order_id = client.place_order(
                variety=client.VARIETY_REGULAR,
                tradingsymbol='SBIN',
                exchange=client.EXCHANGE_NSE,
                transaction_type=client.TRANSACTION_TYPE_SELL,
                quantity=quantity_diff,
                order_type=client.ORDER_TYPE_MARKET,
                product=client.PRODUCT_MIS)
            logging.info("Order placed. ID is: {}".format(order_id))
        except Exception as err:
            logging.error(err)
    elif quantity_diff < 0:
        try:
            order_id = client.place_order(
                variety=client.VARIETY_REGULAR,
                tradingsymbol='SBIN',
                exchange=client.EXCHANGE_NSE,
                transaction_type=client.TRANSACTION_TYPE_BUY,
                quantity=abs(quantity_diff),
                order_type=client.ORDER_TYPE_MARKET,
                product=client.PRODUCT_MIS)
            logging.info("Order placed. ID is: {}".format(order_id))
        except Exception as err:
            logging.error(err)


def mis_mode(server):
    client = server.kite_loginer.get_client()
    kite_trader = server.kite

    def tick():
        orders = client.orders()
        _cancel_pending_orders(client, orders)

        positions = client.positions()
        quantity_diff = positions['day'][0]['day_buy_quantity'] - positions['day'][0]['day_sell_quantity']
        _handle_quantity_diff(client, quantity_diff)

        kite_trader.reset()
        # logging.info('Kite Agent balance and inventory were reset to {}, {}'.format(
        #     kite_trader.balance, kite_trader.inventory))
#104 for improvised def_reset() function in the kite_8.py
        logging.info('Kite Agent balance and inventory were reset to {}, {}, {}, {}, {}, {}'.format(
            kite_trader.balance, kite_trader.inventory, kite_trader._queue, kite_trader.buy_price_queue, kite_trader.sell_price_queue, kite_trader.actions_queue))
        

    return tick
