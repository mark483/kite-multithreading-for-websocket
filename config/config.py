import os

from dotenv import load_dotenv, find_dotenv
from datetime import datetime


class EnvConfig:
    def __init__(self):
        load_dotenv(find_dotenv())

        self.SERVER_HOST = os.environ.get('SERVER_HOST')
        self.SERVER_PORT = os.environ.get('SERVER_PORT')

        self.KITE_API_KEY = os.environ.get("KITE_API_KEY")
        self.KITE_API_SECRET_KEY = os.environ.get("KITE_API_SECRET_KEY")

        self.KITE_USER_ID = os.environ.get('KITE_USER_ID')
        self.KITE_PASSWORD = os.environ.get('KITE_PASSWORD')
        self.KITE_PIN = os.environ.get('KITE_PIN')
        self.KITE_MODEL_PATH = os.environ.get('KITE_MODEL_PATH')
        self.KITE_FREQUENCY = int(os.environ.get('KITE_FREQUENCY'))
        self.KITE_MODE = os.environ.get('KITE_MODE')
        if self.KITE_MODE not in ['CNC', 'MIS', 'CNC_GTT']:
            raise Exception('KITE_MODE should be one of values: CNC or MIS')

        self.KITE_TIME_ZONE = os.environ.get('KITE_TIME_ZONE')
        self.KITE_MIS_TIME = datetime.strptime(os.environ.get('KITE_MIS_TIME'), "%H:%M").time()
        self.WEBSOCKET_KITE_START = datetime.strptime(os.environ.get('WEBSOCKET_KITE_START'), "%H:%M").time()
        self.WEBSOCKET_KITE_END = datetime.strptime(os.environ.get('WEBSOCKET_KITE_END'), "%H:%M").time()
        
        ##CORR_FREQ & MODE
        self.CORR_CALC_FREQ = int(os.environ.get('CORR_CALC_FREQ'))
        self.CORR_MODE = os.environ.get('CORR_MODE')
        
        ##VOL_FREQ
        self.VOL_FREQUENCY = int(os.environ.get('VOL_FREQUENCY'))
        self.VOL_MODE = os.environ.get('VOL_MODE')

        self.BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
        self.BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')
        self.BINANCE_MODEL_PATH = os.environ.get('BINANCE_MODEL_PATH')
