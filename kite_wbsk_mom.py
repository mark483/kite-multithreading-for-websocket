import datetime
import json
import logging
from multiprocessing import Process, Queue

import pytz
import requests
from dotenv import load_dotenv, find_dotenv
from kiteconnect import KiteTicker

from config import EnvConfig

logging.basicConfig(level=logging.DEBUG)


NSE_SBIN_INSTRUMENT_TOKEN = 779521

CLOCK_FREQ = 1

TIME_IN_SEC = 0
CORR_TIME_IN_SEC = 0
#Added for the volatiltiy
VOL_TIME_IN_SEC = 0
EPS = 3

#Muted the URL to send data
UPDATE_TOKEN_URL = 'http://0.0.0.0:8005/kite/update_token'

TRADE_URL = 'http://localhost:8005/kite/trade'
CORR_URL = 'http://localhost:8005/kite/adjust_corr'
CORR_URL_2 = 'http://localhost:8005/kite/adjust_longterm_2'
CORR_URL_STAG = 'http://localhost:8005/kite/adjust_stag'
VOL_URL = 'http://localhost:8005/kite/adjust_volatility'
VOL_URL_3 = 'http://localhost:8005/kite/adjust_volatility_3'
VOL_URL_4 = 'http://localhost:8005/kite/adjust_volatility_4'
REV15_URL = 'http://localhost:8005/kite/adjust_reversal15'
MOM1_URL = 'http://localhost:8005/kite/adjust_mom1'
#Sending data to pnl for trade
#PNL_URL = 'http://localhost:8005/kite/pnl_trade'



def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end

    return start <= x or x <= end


# 0 is Monday, 4 is Friday
def is_weekday(d, start=0, end=4):
    return start <= d.weekday() <= end


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    for tick in ticks:
        token = tick['instrument_token']
        if token != NSE_SBIN_INSTRUMENT_TOKEN:
            logging.error('Instrument tokens are not equal: wait {}, get {}'.format(
                NSE_SBIN_INSTRUMENT_TOKEN, token))
            # ToDo: refresh it and save in db
            return

        if tick['mode'] == 'full':
            traded_time = tick['last_trade_time']

            global CLOCK, CORR_CLOCK, VOL_CLOCK
            # ToDo: add documentation that the method doesn't work with time deltas more than 1 day.
            # Check if it does.

            now = datetime.datetime.now(tz)
            stock_is_open = (time_in_range(TRADE_START, TRADE_END, now.time()) and
                             is_weekday(now))

            if stock_is_open and (traded_time - CORR_CLOCK).seconds > CORR_TIME_IN_SEC - EPS:
                CORR_CLOCK = traded_time
                send_data(CORR_URL, tick)
                
            ## Added the URL for the corrector_2 or adjust_longterm_2
            if stock_is_open and (traded_time - CORR_CLOCK).seconds > CORR_TIME_IN_SEC - EPS:
                CORR_CLOCK = traded_time
                send_data(CORR_URL_2, tick)
                
            ##send data to corrector_stag    
            if stock_is_open and (traded_time - CORR_CLOCK).seconds > CORR_TIME_IN_SEC - EPS:
                CORR_CLOCK = traded_time
                send_data(CORR_URL_STAG, tick)            

            if stock_is_open and (traded_time - CLOCK).seconds > TIME_IN_SEC - EPS:
                CLOCK = traded_time
                send_data(TRADE_URL, tick)
            """
            ## Send data to  pnl            
            if stock_is_open and (traded_time - CLOCK).seconds > TIME_IN_SEC - EPS:
                CLOCK = traded_time
                send_data(PNL_URL, tick)
            """   
            ## Send data to  Volatility   
            if stock_is_open and (traded_time - VOL_CLOCK).seconds > VOL_TIME_IN_SEC - EPS:
                VOL_CLOCK = traded_time
                send_data(VOL_URL, tick)
                
            ## send data to volatiltiy_3
            if stock_is_open and (traded_time - VOL_CLOCK).seconds > VOL_TIME_IN_SEC - EPS:
                VOL_CLOCK = traded_time
                send_data(VOL_URL_3, tick)
                   
            ## send data to volatiltiy_4
            if stock_is_open and (traded_time - VOL_CLOCK).seconds > VOL_TIME_IN_SEC - EPS:
                VOL_CLOCK = traded_time
                send_data(VOL_URL_4, tick)
            
            ## send data to Reversal15
            if stock_is_open and (traded_time - VOL_CLOCK).seconds > VOL_TIME_IN_SEC - EPS:
                VOL_CLOCK = traded_time
                send_data(REV15_URL, tick)
                 
            ## send data to Reversal15
            if stock_is_open and (traded_time - VOL_CLOCK).seconds > VOL_TIME_IN_SEC - EPS:
                VOL_CLOCK = traded_time
                send_data(MOM1_URL, tick)
            
            


def send_data(url, tick):
    traded_time = tick['last_trade_time']
    traded_price = tick['last_price']
    traded_quantity = tick['last_quantity']
    volume = tick['volume']
    logging.info(
        "{}: price - {}, quantity - {}, volume - {}".format(
            traded_time, traded_price, traded_quantity, volume))

    # ToDo: you should run such requests asynchronously
    print(requests.get(url + '?data={}'.format([traded_price])).json())


def on_connect(ws, response):
    # Callback on successful connect.
    ws.subscribe([NSE_SBIN_INSTRUMENT_TOKEN])
    ws.set_mode(ws.MODE_FULL, [NSE_SBIN_INSTRUMENT_TOKEN])


def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()


def on_error(ws, code, error):
    logging.error(error, code)


def run_ticker(q):
    resp = requests.get(UPDATE_TOKEN_URL)
    access_token = json.loads(resp.text)['access_token']

    # Initialise
    kws = KiteTicker(conf.KITE_API_KEY, access_token)
    # Assign the callbacks.
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_error = on_error

    # Infinite loop on the main thread. Nothing after this will run.
    # You have to use the pre-defined callbacks to manage subscriptions.
    kws.connect()
    q.put(0)


if __name__ == '__main__':
    conf = EnvConfig()
    load_dotenv(find_dotenv())

    tz = pytz.timezone(conf.KITE_TIME_ZONE)
    TRADE_START = conf.WEBSOCKET_KITE_START
    TRADE_END = conf.WEBSOCKET_KITE_END

    TIME_IN_SEC = conf.KITE_FREQUENCY * CLOCK_FREQ
    CLOCK = datetime.datetime.now() - datetime.timedelta(seconds=TIME_IN_SEC)

    CORR_TIME_IN_SEC = conf.CORR_CALC_FREQ
    CORR_CLOCK = datetime.datetime.now() - datetime.timedelta(seconds=CORR_TIME_IN_SEC)
    
    VOL_TIME_IN_SEC = conf.VOL_FREQUENCY 
    VOL_CLOCK = datetime.datetime.now() - datetime.timedelta(seconds=VOL_TIME_IN_SEC)

    queue = Queue()
    while True:
        p = Process(target=run_ticker, args=(queue,))
        p.start()
        p.join()  # this blocks until the process terminates
        result = queue.get()
