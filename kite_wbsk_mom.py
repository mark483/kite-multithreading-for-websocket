import datetime
import json
from multiprocessing import Process, Queue
from queuemap import QueueMap
from threading import Thread

import pytz
import requests
from dotenv import load_dotenv, find_dotenv
from kiteconnect import KiteTicker
from kiteconnect import KiteConnect

from config import EnvConfig
from queuemap import QueueMap
from setup_logger import logger


NSE_SBIN_INSTRUMENT_TOKEN = 779521

CLOCK_FREQ = 1

TIME_IN_SEC = 0
CORR_TIME_IN_SEC = 0
#Added for the volatiltiy
VOL_TIME_IN_SEC = 0
EPS = 3

tokens_subset=[]
enclosure_queue = Queue()
qm=QueueMap(window=1)

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

def downloadEnclosures(q):
    """This is the worker thread function.
    It processes items in the queue one after
    another.  These daemon threads go into an
    infinite loop, and only exit when
    the main thread ends.
    """
    while True:
        
        tick = q.get()
        if tick:
            print ('tick received on worker thread')
            #print(tick)
            send_data(tick)
        

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
    print('on tick initiated')
    for tick in ticks:
        #print(tick)
        enclosure_queue.put(tick)
            
            


def send_data(tick):
    instrument_token = tick['instrument_token']
    traded_price = tick['last_price']
    traded_quantity = tick['last_quantity']
    volume = tick['volume']
    qm.set(instrument_token,[traded_price,traded_quantity])
    qm.check_window()
    #c=Corrector(window=30)
    #c.adjust_rocp_factor(tick)


def on_connect(ws, response):
    # Callback on successful connect.
    print('connected')
    global tokens_subset
    print(len(tokens_subset))
    ws.subscribe(tokens_subset)
    #ws.subscribe([NSE_SBIN_INSTRUMENT_TOKEN])
    print('subscribed')
    ws.set_mode(ws.MODE_FULL, tokens_subset)
    #ws.set_mode(ws.MODE_FULL, [NSE_SBIN_INSTRUMENT_TOKEN])
    print('mode set for subscription')


def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()


def on_error(ws, code, error):
    logger.error(error, code)


def run_ticker(q):
    resp = requests.get(UPDATE_TOKEN_URL)
    access_token = json.loads(resp.text)['access_token']

    # Initialise
    kws = KiteTicker(conf.KITE_API_KEY, access_token)
    #get list of tokens
    kite = KiteConnect(api_key=conf.KITE_API_KEY)
    kite.set_access_token(access_token)
    print('retrieving tokens list')
    data=kite.instruments()
    print('list of tokens retrieved')
    #retrive instrument tokens from instruments server response
    tokens = [f['instrument_token'] for f in data]
    #select only 3000 tokens
    global tokens_subset
    tokens_subset=tokens[:3000]
    ###############################################
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

    worker = Thread(target=downloadEnclosures, args=(enclosure_queue,))
    worker.setDaemon(True)
    worker.start()

    queue = Queue()
    while True:
        p = Process(target=run_ticker, args=(queue,))
        p.start()
        p.join()  # this blocks until the process terminates
        result = queue.get()
