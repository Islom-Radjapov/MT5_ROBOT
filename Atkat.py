# import libraries
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sqlite3


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
    df_data = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close']]
    df_data['time'] = pd.to_datetime(df_data['time'], unit='s')
    df_data['candle_type'] = np.vectorize(specify_candle_type)(df_data.open, df_data.close)
    return df_data


def get_signal(data):

    if data.iloc[-2].candle_type == 'bullish':
        if data.iloc[-3].candle_type == 'bearish':
            if data.iloc[-3].open - 0.0015 >= data.iloc[-2].close:
                return 'buy'
            elif data.iloc[-4].candle_type == 'bearish':
                if data.iloc[-4].open - 0.0015 >= data.iloc[-2].close:
                    return 'buy'
                elif data.iloc[-5].candle_type == 'bearish':
                    if data.iloc[-5].open - 0.0015 >= data.iloc[-2].close:
                        return 'buy'
                    elif data.iloc[-6].candle_type == 'bearish':
                        if data.iloc[-6].open - 0.0015 >= data.iloc[-2].close:
                            return 'buy'
                        elif data.iloc[-7].candle_type == 'bearish':
                            if data.iloc[-7].open - 0.0015 >= data.iloc[-2].close:
                                return 'buy'
                            elif data.iloc[-8].candle_type == 'bearish':
                                if data.iloc[-8].open - 0.0015 >= data.iloc[-2].close:
                                    return 'buy'
                                elif data.iloc[-9].candle_type == 'bearish':
                                    if data.iloc[-9].open - 0.0015 >= data.iloc[-2].close:
                                        return 'buy'
                                    elif data.iloc[-10].candle_type == 'bearish':
                                        if data.iloc[-10].open - 0.0015 >= data.iloc[-2].close:
                                            return 'buy'
                                        elif data.iloc[-11].candle_type == 'bearish':
                                            if data.iloc[-11].open - 0.0015 >= data.iloc[-2].close:
                                                return 'buy'

    elif data.iloc[-2].candle_type == 'bearish':
        if data.iloc[-3].candle_type == 'bullish':
            if data.iloc[-3].open + 0.0015 >= data.iloc[-2].close:
                return 'sell'
            elif data.iloc[-4].candle_type == 'bullish':
                if data.iloc[-4].open + 0.0015 >= data.iloc[-2].close:
                    return 'sell'
                elif data.iloc[-5].candle_type == 'bullish':
                    if data.iloc[-5].open + 0.0015 >= data.iloc[-2].close:
                        return 'sell'
                    elif data.iloc[-6].candle_type == 'bullish':
                        if data.iloc[-6].open + 0.0015 >= data.iloc[-2].close:
                            return 'sell'
                        elif data.iloc[-7].candle_type == 'bullish':
                            if data.iloc[-7].open + 0.0015 >= data.iloc[-2].close:
                                return 'sell'
                            elif data.iloc[-8].candle_type == 'bullish':
                                if data.iloc[-8].open + 0.0015 >= data.iloc[-2].close:
                                    return 'sell'
                                elif data.iloc[-9].candle_type == 'bullish':
                                    if data.iloc[-9].open + 0.0015 >= data.iloc[-2].close:
                                        return 'sell'
                                    elif data.iloc[-10].candle_type == 'bullish':
                                        if data.iloc[-10].open + 0.0015 >= data.iloc[-2].close:
                                            return 'sell'
                                        elif data.iloc[-11].candle_type == 'bullish':
                                            if data.iloc[-11].open + 0.0015 >= data.iloc[-2].close:
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
    return order_result[7]


def create_table(symbol):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {symbol} (
                        "id"    INTEGER NOT NULL UNIQUE,
                        "datetime"	TEXT NOT NULL,
                        PRIMARY KEY("id" AUTOINCREMENT)
                        );""")
    connection.commit()
    connection.close()


def add_market(symbol, datetime):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO {symbol} (datetime) VALUES ('{datetime}')")
    connection.commit()
    connection.close()


def get_order(symbol):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    open_time = cursor.execute(f"SELECT datetime FROM {symbol} ORDER BY id DESC ").fetchone()[0]
    connection.commit()
    connection.close()
    return pd.to_datetime(open_time)


initialize = mt5.initialize()

if initialize:
    login = 51494476
    password = 'z0M7R4z7Z'
    server = 'Alpari-MT5-Demo'
    mt5.login(login=login, password=password, server=server)

    print('Connected to MetaTrader5')
    print('Login=>', mt5.account_info().login)
    print('Server=>', mt5.account_info().server)
    print('Balance=>', mt5.account_info().balance)

    # SYMBOLS = ['EURUSD_i', 'GBPUSD_i', 'NZDUSD_i', 'USDCAD_i', 'USDCHF_i', 'AUDUSD_i', 'EURAUD_i', 'EURCAD_i', 'EURCHF_i', 'EURGBP_i', 'GBPAUD_i', 'GBPCAD_i', 'GBPCHF_i', 'USDCAD_i',
    #            'AUDCHF_i', 'AUDNZD_i', 'CADCHF_i', 'AUDCAD_i', 'EURNZD_i', 'NZDCAD_i']
    SYMBOLS = ['EURUSD_i', 'GBPUSD_i', 'NZDUSD_i', 'AUDUSD_i', 'USDCAD_i', 'USDCHF_i']
    TIMEFRAME = mt5.TIMEFRAME_M15
    VOLUME = 0.01
    DEVIATION = 20
    MAGIC = 10

    while True:

        for symbol in SYMBOLS:
            position = positions_get(symbol)
            df = get_df(symbol, TIMEFRAME, 0, 11)
            signal = get_signal(df=df)

            if not position:
                if signal:

                    if signal == 'buy':
                        try:
                            if get_order(symbol) + pd.Timedelta(minutes=15) < datetime.now():
                                tick = mt5.symbol_info_tick(symbol)
                                market_order(symbol=symbol, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC,
                                             stoploss=tick.bid - 0.00033, takeprofit=tick.ask + 0.00077)
                                create_table(symbol)
                                add_market(symbol, datetime.now())
                        except:
                            tick = mt5.symbol_info_tick(symbol)
                            market_order(symbol=symbol, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC,
                                         stoploss=tick.bid - 0.00033, takeprofit=tick.ask + 0.00077)
                            create_table(symbol)
                            add_market(symbol, datetime.now())

                    elif signal == 'sell':
                        try:
                            if get_order(symbol) + pd.Timedelta(minutes=15) < datetime.now():
                                tick = mt5.symbol_info_tick(symbol)
                                market_order(symbol=symbol, volume=VOLUME, order_type="sell", deviation=DEVIATION, magic=MAGIC,
                                             stoploss=tick.ask + 0.00033, takeprofit=tick.bid - 0.00077)
                                create_table(symbol)
                                add_market(symbol, datetime.now())
                        except:
                            tick = mt5.symbol_info_tick(symbol)
                            market_order(symbol=symbol, volume=VOLUME, order_type="sell", deviation=DEVIATION,
                                         magic=MAGIC,
                                         stoploss=tick.ask + 0.00033, takeprofit=tick.bid - 0.00077)
                            create_table(symbol)
                            add_market(symbol, datetime.now())


        time.sleep(1)
else:
    print('No connection')
# Request executed
# Invalid stops