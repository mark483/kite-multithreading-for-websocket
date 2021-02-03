"""
app.py provides routing & falsk server and schedule function for the schedul.py
#99 started the schedule function to clear the orders at the end of the day........

"""
import json
from datetime import datetime, timedelta
# from volatility import Volatility
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from esba import Agent, Model, Deep_Evolution_Strategy
from config import EnvConfig
from schedule import mis_mode
from server import Server, initialize_services

app = Flask(__name__)


@app.route('/', methods=['GET'])
def root():
    return jsonify({'status': 'OK'})


@app.route('/trade', methods=['GET'])
def trade():
    data = json.loads(request.args.get('data'))
    return jsonify(server.binance.trade(data))


@app.route('/kite/trade', methods=['GET'])
def kite_trade():
    data = json.loads(request.args.get('data'))
    return jsonify(server.kite_trade(data))


@app.route('/kite/authorize', methods=['GET'])
def kite_authorize():
    return jsonify({'token': request.args.get('request_token')})


@app.route('/kite/update_token', methods=['GET'])
def kite_update_token():
    access_token = server.kite_loginer.update_access_token()
    return jsonify({'access_token': access_token})


# @app.route('/kite/adjust_corr', methods=['GET'])
# def kite_adjust_corr():
#     data = json.loads(request.args.get('data'))
#     server.corrector.adjust_corr_factor(data)
#     return jsonify({'status': 'OK'})

# @app.route('/kite/adjust_longterm_2', methods=['GET'])
# def kite_adjust_lonterm_2():
#     data = json.loads(request.args.get('data'))
#     server.corrector_2.adjust_longterm_factor(data)
#     return jsonify({'status': 'OK'})

# @app.route('/kite/adjust_stag', methods=['GET'])
# def kite_adjust_stag():
#     data = json.loads(request.args.get('data'))
#     server.corrector_stag.adjust_stag_factor(data)
#     return jsonify({'status': 'OK'})

# @app.route('/kite/adjust_volatility', methods=['GET'])
# def kite_adjust_volatility():
#     data = json.loads(request.args.get('data'))
#     server.volatility.adjust_freq_factor(data)
#     return jsonify({'status': 'OK'})

# @app.route('/kite/adjust_volatility_3', methods=['GET'])
# def kite_adjust_volatility_3():
#     data = json.loads(request.args.get('data'))
#     server.volatility_3.adjust_data(data)
#     return jsonify({'status': 'OK'})

# @app.route('/kite/adjust_volatility_4', methods=['GET'])
# def kite_adjust_volatility_4():
#     data = json.loads(request.args.get('data'))
#     server.volatility_4.run(data)
#     return jsonify({'status': 'OK'})

# @app.route('/kite/adjust_reversal15', methods=['GET'])
# def kite_adjust_reversal15():
#     data = json.loads(request.args.get('data'))
#     server.reversal15.get_data(data)
#     return jsonify({'status': 'OK'})

# @app.route('/kite/adjust_mom1', methods=['GET'])
# def kite_adjust_mom1():
#     data = json.loads(request.args.get('data'))
#     server.mom1.get_data(data)
#     return jsonify({'status': 'OK'})

# ##Added a flask function to send data to pnl
# """
# @app.route('/kite/pnl_trade', methods=['GET'])
# def kite_pnl_trade():
#     data = json.loads(request.args.get('data'))
#     server.pnl.pnl_trade(data)
#     return jsonify({'status': 'OK'})
# """    

@app.route('/kite/access_token', methods=['GET'])
def kite_access_token():
    return jsonify({'access_token': server.kite_loginer.get_access_token()})


if __name__ == '__main__':
    conf = EnvConfig()
    binance_service, kite_service, \
        kite_log_service = initialize_services(conf)#, corrector, corrector_2, volatility, corrector_stag, volatility_3, volatility_4, reversal15, mom1 = initialize_services(conf)

    server = Server(binance_trader=binance_service, kite_trader=kite_service,
                    kite_loginer=kite_log_service) #, corrector=corrector, corrector_2=corrector_2, volatility=volatility, corrector_stag=corrector_stag, volatility_3=volatility_3, volatility_4=volatility_4, reversal15=reversal15, mom1=mom1)

    scheduler = BackgroundScheduler()
#99 Activating the schedule job to clear all orders for the day..........

    if conf.KITE_MODE == 'MIS':
        scheduler.add_job(mis_mode(server),
                            'cron',
                            hour=conf.KITE_MIS_TIME.hour, minute=conf.KITE_MIS_TIME.minute,
                            day_of_week='mon-fri',
                            timezone=conf.KITE_TIME_ZONE)

    scheduler.start()

    try:
        app.run(host=conf.SERVER_HOST, port=conf.SERVER_PORT, debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
