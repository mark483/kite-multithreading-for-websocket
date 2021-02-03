
import binance_api
from binance_api import BinanceTrader
# from corrector import Corrector
# from corrector_2 import Lonterm_corrector_2
# from corrector_stag import Stagnation
# from volatility import Volatility
# from volatility_3 import Volatilitystag
# from volatility_4 import Volatiltiystag4
# from reversal15 import Reversal15
#from mom import Longtermmomentum
# from mom1 import Momentum1min
#from pnl import Monitor_pnl
from esba import load_model
from kite_api import KiteTrader, KiteLogin


class Server:
    def __init__(self, binance_trader, kite_trader, kite_loginer):#, corrector, corrector_2, volatility, corrector_stag, volatility_3, volatility_4, reversal15, mom1):
        self.binance = binance_trader
        self.kite = kite_trader
        self.kite_loginer = kite_loginer
        # self.corrector = corrector
        # self.corrector_2 = corrector_2
        # self.volatility = volatility
        # self.corrector_stag = corrector_stag
        # self.volatility_3  = volatility_3 
        # self.volatility_4  = volatility_4
        # self.reversal15 = reversal15
        # self.mom1 = mom1
        
        
    #    self.pnl = pnl

    def kite_trade(self, data):
        if self.kite.kite_client.access_token is None:
            self.kite_loginer.update_access_token()
        return self.kite.trade(data)


def initialize_services(config):
    agent = load_model(config.BINANCE_MODEL_PATH)
    binance_api.set_keys(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
    binance_trader = BinanceTrader(agent)

    kite_agent = load_model(config.KITE_MODEL_PATH)
    kite = KiteLogin(config.KITE_USER_ID, config.KITE_PASSWORD, config.KITE_API_KEY, config.KITE_PIN,
                     config.KITE_API_SECRET_KEY)
    client = kite.get_client()
    kite_trader = KiteTrader(kite_agent, client, config.KITE_FREQUENCY,
                             product_mode=config.KITE_MODE)
#     #59
#     corrector = Corrector(config.CORR_MODE, 59,
#                           order_mode=config.KITE_MODE) #old window -- config.KITE_FREQUENCY+ 40 # Now window_size == 60 secs
#     #29
#     corrector_stag = Stagnation(config.CORR_MODE, 29,
#                           order_mode=config.KITE_MODE)
#     #119
#     corrector_2 = Lonterm_corrector_2(config.CORR_MODE, 110,
#                         order_mode=config.KITE_MODE) # Now window_size == 120 secs
#     #59
#     volatility = Volatility(config.VOL_MODE, 59,
#                             order_mode=config.KITE_MODE) #old_window -- config.VOL_FREQUENCY + 59 # Now window_size == 60 secs
#     #14 seconds of window
#     volatility_3 = Volatilitystag(config.VOL_MODE, 14,
#                             order_mode=config.KITE_MODE) 
# #    pnl = Monitor_pnl()
#     volatility_4 = Volatiltiystag4( 59, 
#                                    order_mode=config.KITE_MODE)
#     reversal15  = Reversal15 ( 2, 
#                             order_mode=config.KITE_MODE)
    # mom  = Longtermmomentum ( 2, 
    #                     order_mode=config.KITE_MODE)
    # mom1  = Momentum1min ( 2, 
    #                     order_mode=config.KITE_MODE)
    return binance_trader, kite_trader, kite #, corrector, corrector_2, volatility, corrector_stag, volatility_3, volatility_4, reversal15, mom1
