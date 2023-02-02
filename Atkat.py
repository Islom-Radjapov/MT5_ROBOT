# import libraries
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time


def positions_get(symbol):
    return mt5.positions_get(symbol=symbol)


# specify candle type
def specify_candle_type(open_price, close_price):
    if close_price > open_price:
        return 'bullish'
    elif close_price < open_price:
        return 'bearish'
    else:
        return 'doji'

def get_df(symbol, timeframe, start_pos, num_bars):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, num_bars)
    df = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close']]
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['candle_type'] = np.vectorize(specify_candle_type)(df.open, df.close)
    return df


def get_signal(symbol, df):
    symbol_dict = {'EURUSD_i': 0.0015, 'XAUUSD_i': 1.5, 'GBPUSD_i': 0.0015, 'NZDUSD_i': 0.0015, 'USDCAD_i': 0.0015, 'USDCHF_i': 0.0015}

    if df.iloc[-2].candle_type == 'bullish':
        if df.iloc[-3].candle_type == 'bearish':
            if df.iloc[-3].open - symbol_dict[symbol] >= df.iloc[-2].close:
                return 'buy'
            elif df.iloc[-4].candle_type == 'bearish':
                if df.iloc[-4].open - symbol_dict[symbol] >= df.iloc[-2].close:
                    return 'buy'
                elif df.iloc[-5].candle_type == 'bearish':
                    if df.iloc[-5].open - symbol_dict[symbol] >= df.iloc[-2].close:
                        return 'buy'
                    elif df.iloc[-6].candle_type == 'bearish':
                        if df.iloc[-6].open - symbol_dict[symbol] >= df.iloc[-2].close:
                            return 'buy'
                        elif df.iloc[-7].candle_type == 'bearish':
                            if df.iloc[-7].open - symbol_dict[symbol] >= df.iloc[-2].close:
                                return 'buy'
                            elif df.iloc[-8].candle_type == 'bearish':
                                if df.iloc[-8].open - symbol_dict[symbol] >= df.iloc[-2].close:
                                    return 'buy'
                                elif df.iloc[-9].candle_type == 'bearish':
                                    if df.iloc[-9].open - symbol_dict[symbol] >= df.iloc[-2].close:
                                        return 'buy'
                                    elif df.iloc[-10].candle_type == 'bearish':
                                        if df.iloc[-10].open - symbol_dict[symbol] >= df.iloc[-2].close:
                                            return 'buy'
                                        elif df.iloc[-11].candle_type == 'bearish':
                                            if df.iloc[-11].open - symbol_dict[symbol] >= df.iloc[-2].close:
                                                return 'buy'

    elif df.iloc[-2].candle_type == 'bearish':
        if df.iloc[-3].candle_type == 'bullish':
            if df.iloc[-3].open + symbol_dict[symbol] >= df.iloc[-2].close:
                return 'sell'
            elif df.iloc[-4].candle_type == 'bullish':
                if df.iloc[-4].open + symbol_dict[symbol] >= df.iloc[-2].close:
                    return 'sell'
                elif df.iloc[-5].candle_type == 'bullish':
                    if df.iloc[-5].open + symbol_dict[symbol] >= df.iloc[-2].close:
                        return 'sell'
                    elif df.iloc[-6].candle_type == 'bullish':
                        if df.iloc[-6].open + symbol_dict[symbol] >= df.iloc[-2].close:
                            return 'sell'
                        elif df.iloc[-7].candle_type == 'bullish':
                            if df.iloc[-7].open + symbol_dict[symbol] >= df.iloc[-2].close:
                                return 'sell'
                            elif df.iloc[-8].candle_type == 'bullish':
                                if df.iloc[-8].open + symbol_dict[symbol] >= df.iloc[-2].close:
                                    return 'sell'
                                elif df.iloc[-9].candle_type == 'bullish':
                                    if df.iloc[-9].open + symbol_dict[symbol] >= df.iloc[-2].close:
                                        return 'sell'
                                    elif df.iloc[-10].candle_type == 'bullish':
                                        if df.iloc[-10].open + symbol_dict[symbol] >= df.iloc[-2].close:
                                            return 'sell'
                                        elif df.iloc[-11].candle_type == 'bullish':
                                            if df.iloc[-11].open + symbol_dict[symbol] >= df.iloc[-2].close:
                                                return 'sell'


def market_order(symbol, volume, order_type, deviation, magic, stoploss, takeprofit):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "deviation": deviation,
        "magic": magic,
        "sl": stoploss,
        'tp': takeprofit,
        "comment": "python market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    order_result = mt5.order_send(request)
    order_type = {0: 'buy', 1: 'sell'}
    print('SYMBOL=>', symbol, "ORDER=>", order_type[order_result[10].type], "price=>", round(order_result[10].price, 5),
          "stoploss=>", round(order_result[10].sl, 5), "takeprofit=>", round(order_result[10].tp, 5),
          "Result=>", order_result[7])
    return order_result


initialize = mt5.initialize()

if initialize:
    login = 51490382
    password = 'd2L1n5g3b'
    server = 'Alpari-MT5-Demo'
    mt5.login(login=login, password=password, server=server)

    print('Connected to MetaTrader5')
    print('Login=>', mt5.account_info().login)
    print('Server=>', mt5.account_info().server)
    print('Balance=>', mt5.account_info().balance)

    SYMBOLS = ['EURUSD_i',          'XAUUSD_i',        'GBPUSD_i',          'NZDUSD_i',          'USDCAD_i',          'USDCHF_i']
    LOSS =    {'EURUSD_i': 0.00033, 'XAUUSD_i': 0.33,  'GBPUSD_i': 0.00033, 'NZDUSD_i': 0.00033, 'USDCAD_i': 0.00033, 'USDCHF_i': 0.00033}
    PROFIT =  {'EURUSD_i': 0.00075, 'XAUUSD_i': 0.75,  'GBPUSD_i': 0.00075, 'NZDUSD_i': 0.00075, 'USDCAD_i': 0.00075, 'USDCHF_i': 0.00075}
    TIMEFRAME = mt5.TIMEFRAME_M15
    VOLUME = 0.01
    DEVIATION = 20
    MAGIC = 10

    while True:

        for symbol in SYMBOLS:
            position = positions_get(symbol)
            df = get_df(symbol, TIMEFRAME, 0, 11)

            signal = get_signal(symbol=symbol, df=df)

            if not position:
                if signal:
                    tick = mt5.symbol_info_tick(symbol)
                    if signal == 'buy':
                        market_order(symbol=symbol, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC,
                                     stoploss=tick.bid - LOSS[symbol], takeprofit=tick.ask + PROFIT[symbol])

                    elif signal == 'sell':
                        market_order(symbol=symbol, volume=VOLUME, order_type="sell", deviation=DEVIATION, magic=MAGIC,
                                     stoploss=tick.ask + LOSS[symbol], takeprofit=tick.bid - PROFIT[symbol])


        time.sleep(1)
else:
    print('No connection')
