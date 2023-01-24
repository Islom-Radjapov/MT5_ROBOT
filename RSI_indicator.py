import MetaTrader5 as mt5
import pandas as pd
import time


def positions_get(symbol):
    return mt5.positions_get(symbol=symbol)


def get_df(symbol, timeframe, start_pos, num_bars):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, num_bars)
    df = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close']]
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df


def RSI(df, periods, ema = True):
    """
    Returns a pd.Series with the relative strength index.
    """
    close_delta = df['close'].diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    if ema == True:
        # Use exponential moving average
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        # Use simple moving average
        ma_up = up.rolling(window=periods, adjust=False).mean()
        ma_down = down.rolling(window=periods, adjust=False).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    return rsi.values[-1]


def ATR(df, period):
    # calculating the range of each candle
    df['range'] = df['high'] - df['low']

    # calculating the average value of ranges
    df['atr_14'] = df['range'].rolling(period).mean()

    return df['atr_14'].values[-1]


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
    print("ORDER=>", order_type[order_result[10].type], "price=>", round(order_result[10].price, 5),    # "stoploss=>", round(order_result[10].sl, 5),
          "takeprofit=>", round(order_result[10].tp, 5), "Result=>", order_result[7])
    return order_result


def add_order(symbol, volume, order_type, deviation, magic, stoploss, takeprofit):
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
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    order_result = mt5.order_send(request)
    order_type = {0: 'buy', 1: 'sell'}
    print("ADD ORDER=>", order_type[order_result[10].type], "price=>", round(order_result[10].price, 5),    # "stoploss=>", round(order_result[10].sl, 5),
          "takeprofit=>", round(order_result[10].tp, 5), "Result=>", order_result[7])
    return order_result

def get_new_volume(volum):
    if volum == 0.01:
        return 0.02
    elif volum == 0.02:
        return 0.03
    elif volum == 0.03:
        return 0.05
    elif volum == 0.05:
        return 0.08
    elif volum == 0.08:
        return 0.13
    elif volum == 0.13:
        return 0.21
    elif volum == 0.21:
        return 0.33
    elif volum == 0.33:
        return 0.54
    elif volum == 0.54:
        return 0.87
    elif volum == 0.87:
        return 1.41
    elif volum == 1.41:
        return 2.28
    elif volum == 2.28:
        return 3.68
    elif volum == 3.68:
        return 5.96
    elif volum == 5.96:
        return 9.64


# def trading_takeprofit(position, tick):
#
#     if position.type == 1:  # sell
#         if tick.ask - position.tp <= 0.0001:
#             tp = tick.ask + 0.0002
#             sl = tick.ask + 0.0002
#             request = {
#                 "action": mt5.TRADE_ACTION_SLTP,
#                 "symbol": position.symbol,
#                 "volume": position.volume,
#                 "type": position.type,
#                 "position": position.ticket,
#                 "price_open": position.price_open,
#                 "sl": sl,
#                 "tp": tp,
#                 "magic": position.magic,
#                 "comment": "python script open",
#                 "type_time": mt5.ORDER_TIME_GTC,
#                 "type_filling": mt5.ORDER_FILLING_FOK,
#                 "ENUM_ORDER_STATE": mt5.ORDER_FILLING_RETURN,
#             }
#
#             result = mt5.order_send(request)
#             print("Profit")
#             return result
#
#
#     elif position.type == 0: # buy
#         distance = abs(round(position.tp - tick.ask, 5))
#         if distance <= 0.0001:
#             tp = tick.ask + 0.0002
#             sl = tick.bid - 0.0002
#             request = {
#                 "action": mt5.TRADE_ACTION_SLTP,
#                 "symbol": position.symbol,
#                 "volume": position.volume,
#                 "type": position.type,
#                 "position": position.ticket,
#                 "price_open": position.price_open,
#                 "sl": sl,
#                 "tp": tp,
#                 "magic": position.magic,
#                 "comment": "python script open",
#                 "type_time": mt5.ORDER_TIME_GTC,
#                 "type_filling": mt5.ORDER_FILLING_FOK,
#                 "ENUM_ORDER_STATE": mt5.ORDER_FILLING_RETURN,
#             }
#
#             result = mt5.order_send(request)
#             print("Profit")
#             return result


initialize = mt5.initialize()

if initialize:
    login = 51466985
    password = 'N4ry9n7vi'
    server = 'Alpari-MT5-Demo'
    mt5.login(login=login, password=password, server=server)

    print('Connected to MetaTrader5')
    print('Login=>' , mt5.account_info().login)
    print('Server=>', mt5.account_info().server)
    print('Balance=>', mt5.account_info().balance)


    SYMBOL = "EURUSD_i"
    TIMEFRAME = mt5.TIMEFRAME_M5
    PERIOD = 14  # setting the RSI and ATR Period
    VOLUME = 0.01
    PIPS = 0.0005
    DEVIATION = 20
    MAGIC = 10

    while True:

        position = positions_get(SYMBOL)
        tick = mt5.symbol_info_tick(SYMBOL)
        df = get_df(SYMBOL, TIMEFRAME, 0, 24)
        atr = ATR(df, PERIOD)

        # order yoq bosa rsi tekshirib tog'ri kesa order ochadi
        if not position:
            rsi = RSI(df, PERIOD)
            if rsi < 35:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="buy", deviation=DEVIATION, magic=MAGIC,
                             stoploss=0.0, takeprofit=tick.ask + atr)
            elif rsi > 65:
                market_order(symbol=SYMBOL, volume=VOLUME, order_type="sell", deviation=DEVIATION, magic=MAGIC,
                             stoploss=0.0, takeprofit=tick.bid - atr)

        else:
            position = position[0]
            if position.type == 1:          # sell
                if position.price_open + PIPS <= tick.bid:  # # 50 pip minusga kirsa yana sell ochadi
                    new_volume = get_new_volume(position.volume)
                    add_order(symbol=SYMBOL, volume=new_volume, order_type="sell", deviation=DEVIATION, magic=MAGIC, takeprofit=tick.bid - atr, stoploss=0.0)

            elif position.type == 0:        # buy
                if position.price_open - PIPS >= tick.ask:  # 50 pip minusga kirsa yana buy ochadi
                    new_volume = get_new_volume(position.volume)
                    add_order(symbol=SYMBOL, volume=new_volume, order_type="buy", deviation=DEVIATION, magic=MAGIC, takeprofit=tick.bid + atr, stoploss=0.0)
            # else:
            #     trading_takeprofit(position=position, tick=tick)
        time.sleep(1)
else:
    print('No connection')

